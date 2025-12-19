from django.contrib import admin
from .models import WikiArticle, WikiImage, WikiFile, WikiViewGroup


@admin.register(WikiViewGroup)
class WikiViewGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['users']


@admin.register(WikiArticle)
class WikiArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'parent', 'order', 'author', 'is_published', 'visibility_type', 'created_at']
    list_filter = ['is_published', 'visibility_type', 'created_at', 'author']
    search_fields = ['title', 'content']
    raw_id_fields = ['parent', 'author']
    filter_horizontal = ['view_groups']


@admin.register(WikiImage)
class WikiImageAdmin(admin.ModelAdmin):
    list_display = ['article', 'alt_text', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['article__title', 'alt_text']


@admin.register(WikiFile)
class WikiFileAdmin(admin.ModelAdmin):
    list_display = ['article', 'name', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['article__title', 'name', 'description']

