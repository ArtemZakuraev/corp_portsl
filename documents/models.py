import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Document(models.Model):
    """
    Документ в общем хранилище /data с базовыми правами доступа.
    Физически файлы хранятся в DATA_ROOT (напр. примонтированный диск /data).
    """

    ACCESS_AUTHOR = "author"
    ACCESS_ASSIGNED = "assigned"
    ACCESS_EVERYONE = "everyone"

    ACCESS_CHOICES = [
        (ACCESS_AUTHOR, "Только автор (и его руководитель)"),
        (ACCESS_ASSIGNED, "Назначенные пользователи (и руководители)"),
        (ACCESS_EVERYONE, "Все пользователи"),
    ]

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Автор",
    )
    name = models.CharField(max_length=255, verbose_name="Название файла")
    description = models.TextField(blank=True, verbose_name="Описание")

    # относительный путь от DATA_ROOT, чтобы можно было легко менять корень
    relative_path = models.CharField(max_length=500, unique=True, verbose_name="Путь в /data")

    size = models.BigIntegerField(verbose_name="Размер (байты)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    access_level = models.CharField(
        max_length=20,
        choices=ACCESS_CHOICES,
        default=ACCESS_AUTHOR,
        verbose_name="Права доступа",
    )

    assigned_users = models.ManyToManyField(
        User,
        related_name="assigned_documents",
        blank=True,
        verbose_name="Назначенные пользователи",
    )

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self) -> str:  # type: ignore[override]
        return self.name

    @property
    def absolute_path(self) -> str:
        return os.path.join(str(settings.DATA_ROOT), self.relative_path)










