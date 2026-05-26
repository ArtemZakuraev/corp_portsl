"""Wiki app admin configuration."""
from django.contrib import admin
from .models import WikiArticle, WikiCategory, WikiAttachment


@admin.register(WikiCategory)
class WikiCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'created_at')
    list_filter = ('parent', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(WikiArticle)
class WikiArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'is_published', 'is_featured', 'views', 'version', 'updated_at')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author', 'category', 'parent_article')
    date_hierarchy = 'updated_at'
    ordering = ('-updated_at',)
    filter_horizontal = ()


@admin.register(WikiAttachment)
class WikiAttachmentAdmin(admin.ModelAdmin):
    list_display = ('article', 'file', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    raw_id_fields = ('article', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
