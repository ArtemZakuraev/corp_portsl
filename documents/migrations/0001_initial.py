from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Document",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="Название файла")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("relative_path", models.CharField(max_length=500, unique=True, verbose_name="Путь в /data")),
                ("size", models.BigIntegerField(verbose_name="Размер (байты)")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Дата изменения")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")),
                (
                    "access_level",
                    models.CharField(
                        choices=[
                            ("author", "Только автор (и его руководитель)"),
                            ("assigned", "Назначенные пользователи (и руководители)"),
                            ("everyone", "Все пользователи"),
                        ],
                        default="author",
                        max_length=20,
                        verbose_name="Права доступа",
                    ),
                ),
                (
                    "assigned_users",
                    models.ManyToManyField(
                        blank=True,
                        related_name="assigned_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Назначенные пользователи",
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ",
                "verbose_name_plural": "Документы",
            },
        ),
    ]










