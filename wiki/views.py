"""Wiki app views with optimized queries."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import WikiArticle, WikiCategory, WikiAttachment


@login_required
def article_list(request):
    """List all published wiki articles."""
    queryset = WikiArticle.objects.select_related(
        'author', 'category'
    ).filter(is_published=True)

    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(excerpt__icontains=search_query)
        )

    # Featured only
    if request.GET.get('featured'):
        queryset = queryset.filter(is_featured=True)

    paginator = Paginator(queryset, 15)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    categories = WikiCategory.objects.all()

    context = {
        'articles': articles,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'is_featured': request.GET.get('featured'),
    }
    return render(request, 'wiki/article_list.html', context)


@login_required
def article_detail(request, slug):
    """Wiki article detail view."""
    article = get_object_or_404(
        WikiArticle.objects.select_related(
            'author', 'category'
        ).prefetch_related(
            'attachments',
            'child_articles'
        ),
        slug=slug,
        is_published=True
    )
    article.increment_views()

    related_articles = article.get_related_articles()

    context = {
        'article': article,
        'related_articles': related_articles,
    }
    return render(request, 'wiki/article_detail.html', context)


@login_required
def create_article(request):
    """Create new wiki article."""
    if request.method == 'POST':
        article = WikiArticle.objects.create(
            title=request.POST.get('title'),
            slug=request.POST.get('slug'),
            content=request.POST.get('content'),
            excerpt=request.POST.get('excerpt', ''),
            author=request.user,
            category_id=request.POST.get('category'),
            parent_article_id=request.POST.get('parent_article') or None,
            is_published=request.POST.get('is_published') == 'on',
            is_featured=request.POST.get('is_featured') == 'on',
        )
        return redirect('wiki:detail', slug=article.slug)
    
    categories = WikiCategory.objects.all()
    return render(request, 'wiki/article_form.html', {
        'categories': categories,
        'article': None,
    })


@login_required
def edit_article(request, slug):
    """Edit existing wiki article."""
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.method == 'POST':
        article.title = request.POST.get('title')
        article.slug = request.POST.get('slug')
        article.content = request.POST.get('content')
        article.excerpt = request.POST.get('excerpt', '')
        article.category_id = request.POST.get('category')
        article.parent_article_id = request.POST.get('parent_article') or None
        article.is_published = request.POST.get('is_published') == 'on'
        article.is_featured = request.POST.get('is_featured') == 'on'
        article.version += 1
        article.save()
        return redirect('wiki:detail', slug=article.slug)
    
    categories = WikiCategory.objects.all()
    return render(request, 'wiki/article_form.html', {
        'article': article,
        'categories': categories,
    })


@login_required
@require_http_methods(["POST"])
def upload_attachment(request, slug):
    """Upload file attachment to article."""
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.FILES.get('file'):
        attachment = WikiAttachment.objects.create(
            article=article,
            file=request.FILES.get('file'),
            uploaded_by=request.user
        )
        return JsonResponse({
            'success': True,
            'file_url': attachment.file.url,
            'file_name': attachment.file.name
        })
    
    return JsonResponse({'success': False}, status=400)
