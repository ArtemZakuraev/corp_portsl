import uuid

from django.conf import settings
from django.db import models


class Task(models.Model):
    """
    Задача, которую можно назначить пользователю по email.
    Для доступа без регистрации используется токен.
    """

    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("done", "Выполнена"),
    ]

    PRIORITY_CHOICES = [
        ("important", "Важно"),
        ("urgent", "Срочно"),
        ("critical", "Критично"),
    ]

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name="Название задачи")
    description = models.TextField(verbose_name="Описание задачи", blank=True)
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        null=True,
        blank=True,
        verbose_name="Важность",
        help_text="Выберите уровень важности задачи.",
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks",
        verbose_name="Исполнитель (пользователь системы)",
    )
    assignee_email = models.EmailField(
        verbose_name="Email исполнителя",
        help_text="Используется для отправки ссылки на задачу, даже если пользователь не зарегистрирован.",
    )

    token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        verbose_name="Токен внешнего доступа",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="Срок выполнения")
    reminder_sent = models.BooleanField(
        default=False,
        verbose_name="Напоминание отправлено",
        help_text="Отмечается после отправки email-напоминания по сроку задачи.",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
        verbose_name="Постановщик",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создана")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлена")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"

    def __str__(self) -> str:  # type: ignore[override]
        return self.title



