from django.conf import settings
from django.db import models


class News(models.Model):
    """
    Корпоративная новость.
    Публикуется модераторами, последняя новость уходит по email всем сотрудникам.
    """

    title = models.CharField(max_length=255, verbose_name="Тема")
    body = models.TextField(
        verbose_name="Текст новости (поддерживается HTML-разметка)",
        help_text="Можно использовать базовую HTML-разметку для заголовков, списков и изображений.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="news",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # type: ignore[override]
        return self.title


class NewsImage(models.Model):
    """
    Изображение, прикреплённое к новости.
    Поддерживаются форматы: JPG, PNG, GIF, WebP.
    """

    news = models.ForeignKey(
        News,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Новость",
    )
    image = models.ImageField(
        upload_to="news/images/",
        verbose_name="Изображение",
        help_text="Загрузите изображение в формате JPG, PNG, GIF или WebP.",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Альтернативный текст",
        help_text="Описание изображения для доступности (alt-текст).",
    )

    class Meta:
        verbose_name = "Изображение новости"
        verbose_name_plural = "Изображения новостей"
        ordering = ["uploaded_at"]

    def __str__(self) -> str:  # type: ignore[override]
        return f"Изображение для {self.news.title}"
