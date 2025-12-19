from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=255, verbose_name="Название задачи")),
                ("description", models.TextField(blank=True, verbose_name="Описание задачи")),
                (
                    "assignee_email",
                    models.EmailField(
                        help_text="Используется для отправки ссылки на задачу, даже если пользователь не зарегистрирован.",
                        max_length=254,
                        verbose_name="Email исполнителя",
                    ),
                ),
                (
                    "token",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        unique=True,
                        verbose_name="Токен внешнего доступа",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "Новая"), ("in_progress", "В работе"), ("done", "Выполнена")],
                        default="new",
                        max_length=20,
                        verbose_name="Статус",
                    ),
                ),
                ("due_date", models.DateField(blank=True, null=True, verbose_name="Срок выполнения")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создана")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлена")),
                (
                    "assignee",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Исполнитель (пользователь системы)",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="created_tasks",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Постановщик",
                    ),
                ),
            ],
            options={
                "verbose_name": "Задача",
                "verbose_name_plural": "Задачи",
            },
        ),
    ]










