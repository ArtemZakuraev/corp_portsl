"""News app views."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import News, NewsCategory


@login_required
def news_list(request):
    """List all published news."""
    queryset = News.objects.select_related('author', 'category').filter(is_published=True)
    
    # Category filter
    category_slug = request.GET.get('category')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query)
        )
    
    paginator = Paginator(queryset, 10)
    page = request.GET.get('page')
    news_items = paginator.get_page(page)
    categories = NewsCategory.objects.all()
    
    context = {
        'news_items': news_items,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'news/news_list.html', context)


@login_required
def news_detail(request, pk):
    """News detail view."""
    news_item = get_object_or_404(
        News.objects.select_related('author', 'category'),
        pk=pk,
        is_published=True
    )
    news_item.increment_views()
    
    # Related news
    related_news = News.objects.filter(
        category=news_item.category,
        is_published=True
    ).exclude(pk=news_item.pk)[:3]
    
    context = {
        'news_item': news_item,
        'related_news': related_news,
    }
    return render(request, 'news/news_detail.html', context)
