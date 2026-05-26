"""News app for corporate portal - Company announcements and updates."""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class NewsCategory(models.Model):
    """Categories for news organization."""
    
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Название категории'))
    slug = models.SlugField(unique=True, verbose_name=_('Слаг'))
    color = models.CharField(max_length=7, default='#4f46e5', help_text='Hex цвет', verbose_name=_('Цвет'))
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Категория новостей')
        verbose_name_plural = _('Категории новостей')
    
    def __str__(self):
        return self.name


class News(models.Model):
    """News/Announcement model."""
    
    title = models.CharField(max_length=300, verbose_name=_('Заголовок'))
    content = models.TextField(verbose_name=_('Содержание'))
    excerpt = models.TextField(blank=True, help_text=_('Краткое описание'), verbose_name=_('Анонс'))
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='news_articles', verbose_name=_('Автор'))
    category = models.ForeignKey(NewsCategory, on_delete=models.SET_NULL, null=True, related_name='news', verbose_name=_('Категория'))
    image = models.ImageField(upload_to='news/', null=True, blank=True, verbose_name=_('Изображение'))
    
    is_published = models.BooleanField(default=False, verbose_name=_('Опубликовано'))
    is_pinned = models.BooleanField(default=False, help_text=_('Закрепить вверху списка'), verbose_name=_('Закреплено'))
    send_email = models.BooleanField(default=False, help_text=_('Отправить уведомление по email'), verbose_name=_('Отправить email'))
    
    views = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    published_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Дата публикации'))
    
    class Meta:
        ordering = ['-is_pinned', '-published_at', '-created_at']
        verbose_name = _('Новость')
        verbose_name_plural = _('Новости')
        indexes = [
            models.Index(fields=['-is_pinned', '-published_at']),
            models.Index(fields=['is_published', '-published_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment view counter."""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])
