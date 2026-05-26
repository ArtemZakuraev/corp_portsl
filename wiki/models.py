"""
Wiki app models - Knowledge base and documentation.
Optimized with proper indexing, full-text search support, and versioning.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinLengthValidator


class WikiCategory(models.Model):
    """Categories for organizing wiki articles."""
    
    name = models.CharField(max_length=200, unique=True, verbose_name=_('Название'))
    slug = models.SlugField(unique=True, verbose_name=_('Слаг'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительская категория')
    )
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Иконка FontAwesome (например, fa-book)'),
        verbose_name=_('Иконка')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return self.name


class WikiArticle(models.Model):
    """Wiki article model with versioning support."""
    
    title = models.CharField(
        max_length=300,
        verbose_name=_('Заголовок'),
        validators=[MinLengthValidator(3)]
    )
    slug = models.SlugField(unique=True, verbose_name=_('Слаг'))
    content = models.TextField(verbose_name=_('Содержание'))
    excerpt = models.TextField(
        blank=True,
        help_text=_('Краткое описание для превью'),
        verbose_name=_('Анонс')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='wiki_articles',
        verbose_name=_('Автор')
    )
    category = models.ForeignKey(
        WikiCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name=_('Категория')
    )
    parent_article = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='child_articles',
        verbose_name=_('Родительская статья')
    )
    
    is_published = models.BooleanField(default=False, verbose_name=_('Опубликовано'))
    is_featured = models.BooleanField(
        default=False,
        help_text=_('Показывать на главной странице'),
        verbose_name=_('Избранное')
    )
    
    views = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))
    version = models.PositiveIntegerField(default=1, verbose_name=_('Версия'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        ordering = ['-is_featured', '-updated_at']
        verbose_name = _('Статья')
        verbose_name_plural = _('Статьи')
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', '-updated_at']),
            models.Index(fields=['is_published', '-updated_at']),
            models.Index(fields=['-views']),
        ]
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        """Increment view counter."""
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])
    
    def get_related_articles(self, limit=3):
        """Get related articles from the same category."""
        if self.category:
            return WikiArticle.objects.filter(
                category=self.category,
                is_published=True
            ).exclude(pk=self.pk)[:limit]
        return WikiArticle.objects.none()


class WikiAttachment(models.Model):
    """File attachments for wiki articles."""
    
    article = models.ForeignKey(
        WikiArticle,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Статья')
    )
    file = models.FileField(upload_to='wiki_attachments/', verbose_name=_('Файл'))
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Загрузил')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата загрузки'))
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Вложение')
        verbose_name_plural = _('Вложения')
        indexes = [
            models.Index(fields=['article', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.file.name} ({self.article.title})"
