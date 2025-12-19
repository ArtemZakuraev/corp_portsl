from django.conf import settings
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Invitation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("token", models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("expires_at", models.DateTimeField()),
                (
                    "email_hint",
                    models.EmailField(
                        blank=True,
                        help_text="Необязательно. Можно указать, если приглашение предназначено для конкретного человека.",
                        max_length=254,
                        null=True,
                        verbose_name="Рекомендуемый email",
                    ),
                ),
                ("used_at", models.DateTimeField(blank=True, null=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="created_invitations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Создано пользователем",
                    ),
                ),
                (
                    "used_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="used_invitations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Использовано пользователем",
                    ),
                ),
            ],
            options={
                "verbose_name": "Пригласительная ссылка",
                "verbose_name_plural": "Пригласительные ссылки",
            },
        ),
    ]










