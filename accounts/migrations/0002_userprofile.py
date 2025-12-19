from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="Фамилия")),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="Имя")),
                ("middle_name", models.CharField(blank=True, max_length=150, verbose_name="Отчество")),
                ("department", models.CharField(blank=True, max_length=255, verbose_name="Департамент")),
                ("unit", models.CharField(blank=True, max_length=255, verbose_name="Отдел")),
                ("position", models.CharField(blank=True, max_length=255, verbose_name="Должность")),
                ("phone_personal", models.CharField(blank=True, max_length=50, verbose_name="Личный телефон")),
                ("phone_internal", models.CharField(blank=True, max_length=20, verbose_name="Внутренний телефон")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Профиль пользователя",
                "verbose_name_plural": "Профили пользователей",
            },
        ),
    ]










