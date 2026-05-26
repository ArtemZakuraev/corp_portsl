"""News admin configuration."""
from django.contrib import admin
from .models import News, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'is_published', 'is_pinned', 'views', 'published_at']
    list_filter = ['is_published', 'is_pinned', 'category', 'send_email']
    search_fields = ['title', 'content', 'excerpt']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'excerpt', 'content', 'author', 'category')
        }),
        ('Изображение', {
            'fields': ('image',)
        }),
        ('Публикация', {
            'fields': ('is_published', 'is_pinned', 'published_at', 'send_email')
        }),
        ('Статистика', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
