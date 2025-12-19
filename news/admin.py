from django.contrib import admin
from .models import News, NewsImage


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "created_at"]
    list_filter = ["created_at", "author"]
    search_fields = ["title", "body"]
    readonly_fields = ["created_at"]


@admin.register(NewsImage)
class NewsImageAdmin(admin.ModelAdmin):
    list_display = ["news", "uploaded_at", "alt_text"]
    list_filter = ["uploaded_at"]
    search_fields = ["news__title", "alt_text"]
    readonly_fields = ["uploaded_at"]
