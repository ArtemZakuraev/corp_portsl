from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404, FileResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import os
import uuid
from django.conf import settings

from .models import WikiArticle, WikiImage, WikiFile, WikiViewGroup
from .forms import WikiArticleForm, WikiImageForm, WikiFileForm, WikiViewGroupForm


def _is_wiki_moderator(user):
    """Проверяет, является ли пользователь модератором базы знаний."""
    if not user.is_authenticated:
        return False
    try:
        return user.profile.is_wiki_moderator
    except:
        return False


def wiki_list(request):
    """
    Список всех статей базы знаний.
    Отображает иерархическую структуру статей.
    Фильтрует статьи по правам доступа пользователя.
    """
    # Получаем все опубликованные корневые статьи
    all_articles = WikiArticle.objects.filter(
        is_published=True,
        parent__isnull=True
    ).prefetch_related('children', 'view_groups').order_by('order', 'title')
    
    # Фильтруем статьи по правам доступа
    articles = []
    for article in all_articles:
        if article.can_view(request.user):
            articles.append(article)
    
    return render(
        request,
        'wiki/wiki_list.html',
        {
            'articles': articles,
            'is_moderator': _is_wiki_moderator(request.user),
        }
    )


def wiki_article(request, slug):
    """
    Просмотр конкретной статьи базы знаний.
    Проверяет права доступа пользователя.
    """
    article = get_object_or_404(WikiArticle, slug=slug, is_published=True)
    
    # Проверяем права доступа
    if not article.can_view(request.user):
        if not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated:
            messages.error(request, 'Для просмотра этой статьи необходимо войти в систему.')
            return redirect('login')
        else:
            raise Http404("У вас нет доступа к этой статье.")
    
    # Получаем дочерние статьи (только те, к которым есть доступ)
    all_children = article.children.filter(is_published=True).order_by('order', 'title')
    children = [child for child in all_children if child.can_view(request.user)]
    
    # Получаем все статьи для содержания (только корневые) с дочерними
    all_root_articles = WikiArticle.objects.filter(
        is_published=True,
        parent__isnull=True
    ).prefetch_related('children', 'view_groups').order_by('order', 'title')
    
    # Фильтруем по правам доступа
    all_articles = [art for art in all_root_articles if art.can_view(request.user)]
    
    return render(
        request,
        'wiki/wiki_article.html',
        {
            'article': article,
            'children': children,
            'all_articles': all_articles,
            'breadcrumbs': article.get_breadcrumbs(),
            'is_moderator': _is_wiki_moderator(request.user),
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_create(request):
    """
    Создание новой статьи базы знаний.
    Доступно только модераторам.
    """
    if request.method == 'POST':
        form = WikiArticleForm(request.POST, user=request.user)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            
            # Обработка загрузки изображений
            if 'images' in request.FILES:
                for image_file in request.FILES.getlist('images'):
                    WikiImage.objects.create(
                        article=article,
                        image=image_file
                    )
            
            # Обработка загрузки файлов
            if 'files' in request.FILES:
                for file_obj in request.FILES.getlist('files'):
                    WikiFile.objects.create(
                        article=article,
                        file=file_obj
                    )
            
            return redirect('wiki_article', slug=article.slug)
    else:
        form = WikiArticleForm(user=request.user)
    
    # Получаем все статьи для выбора родителя
    all_articles = WikiArticle.objects.filter(is_published=True).order_by('title')
    
    return render(
        request,
        'wiki/wiki_form.html',
        {
            'form': form,
            'all_articles': all_articles,
            'action': 'create',
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_edit(request, slug):
    """
    Редактирование статьи базы знаний.
    Доступно только модераторам.
    """
    article = get_object_or_404(WikiArticle, slug=slug)
    
    if request.method == 'POST':
        form = WikiArticleForm(request.POST, instance=article, user=request.user)
        if form.is_valid():
            article = form.save()
            
            # Обработка загрузки новых изображений
            if 'images' in request.FILES:
                for image_file in request.FILES.getlist('images'):
                    WikiImage.objects.create(
                        article=article,
                        image=image_file
                    )
            
            # Обработка загрузки новых файлов
            if 'files' in request.FILES:
                for file_obj in request.FILES.getlist('files'):
                    WikiFile.objects.create(
                        article=article,
                        file=file_obj
                    )
            
            return redirect('wiki_article', slug=article.slug)
    else:
        form = WikiArticleForm(instance=article, user=request.user)
    
    # Получаем все статьи для выбора родителя
    all_articles = WikiArticle.objects.filter(is_published=True).exclude(id=article.id).order_by('title')
    
    return render(
        request,
        'wiki/wiki_form.html',
        {
            'form': form,
            'article': article,
            'all_articles': all_articles,
            'action': 'edit',
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_delete_image(request, image_id):
    """Удаление изображения из статьи."""
    image = get_object_or_404(WikiImage, id=image_id)
    article_slug = image.article.slug
    image.delete()
    return redirect('wiki_edit', slug=article_slug)


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_delete_file(request, file_id):
    """Удаление файла из статьи."""
    file_obj = get_object_or_404(WikiFile, id=file_id)
    article_slug = file_obj.article.slug
    file_obj.delete()
    return redirect('wiki_edit', slug=article_slug)


def wiki_file_download(request, file_id):
    """Скачивание файла из статьи."""
    file_obj = get_object_or_404(WikiFile, id=file_id)
    
    if not file_obj.article.is_published:
        raise Http404("Файл не найден")
    
    # Проверяем права доступа
    if not file_obj.article.can_view(request.user):
        if not hasattr(request.user, 'is_authenticated') or not request.user.is_authenticated:
            messages.error(request, 'Для скачивания файла необходимо войти в систему.')
            return redirect('login')
        else:
            raise Http404("У вас нет доступа к этому файлу.")
    
    file_path = file_obj.file.path
    if not os.path.exists(file_path):
        raise Http404("Файл не найден")
    
    return FileResponse(
        open(file_path, 'rb'),
        filename=file_obj.get_file_name(),
        as_attachment=True
    )


# Views для управления группами просмотра
@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_groups_list(request):
    """
    Список групп просмотра.
    Доступно только модераторам.
    """
    groups = WikiViewGroup.objects.all().prefetch_related('users').order_by('name')
    
    return render(
        request,
        'wiki/wiki_groups.html',
        {
            'groups': groups,
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_group_create(request):
    """
    Создание новой группы просмотра.
    Доступно только модераторам.
    """
    if request.method == 'POST':
        form = WikiViewGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Группа "{group.name}" успешно создана.')
            return redirect('wiki_groups_list')
    else:
        form = WikiViewGroupForm()
    
    return render(
        request,
        'wiki/wiki_group_form.html',
        {
            'form': form,
            'action': 'create',
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_group_edit(request, group_id):
    """
    Редактирование группы просмотра.
    Доступно только модераторам.
    """
    group = get_object_or_404(WikiViewGroup, id=group_id)
    
    if request.method == 'POST':
        form = WikiViewGroupForm(request.POST, instance=group)
        if form.is_valid():
            group = form.save()
            messages.success(request, f'Группа "{group.name}" успешно обновлена.')
            return redirect('wiki_groups_list')
    else:
        form = WikiViewGroupForm(instance=group)
    
    return render(
        request,
        'wiki/wiki_group_form.html',
        {
            'form': form,
            'group': group,
            'action': 'edit',
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
def wiki_group_delete(request, group_id):
    """
    Удаление группы просмотра.
    Доступно только модераторам.
    """
    group = get_object_or_404(WikiViewGroup, id=group_id)
    
    if request.method == 'POST':
        group_name = group.name
        group.delete()
        messages.success(request, f'Группа "{group_name}" успешно удалена.')
        return redirect('wiki_groups_list')
    
    return render(
        request,
        'wiki/wiki_group_delete.html',
        {
            'group': group,
        }
    )


@login_required
@user_passes_test(_is_wiki_moderator)
@csrf_exempt
@require_http_methods(["POST"])
def wiki_upload_image(request):
    """
    Загрузка изображения для редактора TinyMCE.
    Доступно только модераторам.
    """
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    file = request.FILES['file']
    
    # Проверяем тип файла
    if not file.content_type.startswith('image/'):
        return JsonResponse({'error': 'File is not an image'}, status=400)
    
    # Генерируем уникальное имя файла
    file_ext = os.path.splitext(file.name)[1]
    file_name = f"{uuid.uuid4()}{file_ext}"
    
    # Сохраняем файл в media/wiki/images/
    upload_path = os.path.join(settings.MEDIA_ROOT, 'wiki', 'images', file_name)
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    
    with open(upload_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    # Возвращаем URL изображения
    image_url = f"{settings.MEDIA_URL}wiki/images/{file_name}"
    
    return JsonResponse({'location': image_url})

