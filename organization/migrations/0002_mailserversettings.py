from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MailServerSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("host", models.CharField(default="smtp.example.com", max_length=255, verbose_name="SMTP хост")),
                ("port", models.PositiveIntegerField(default=587, verbose_name="SMTP порт")),
                ("use_tls", models.BooleanField(default=True, verbose_name="Использовать TLS")),
                ("use_ssl", models.BooleanField(default=False, verbose_name="Использовать SSL")),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Имя пользователя",
                    ),
                ),
                (
                    "password",
                    models.CharField(blank=True, max_length=255, null=True, verbose_name="Пароль"),
                ),
                (
                    "from_email",
                    models.EmailField(
                        default="no-reply@example.com",
                        max_length=254,
                        verbose_name="Email отправителя",
                    ),
                ),
            ],
            options={
                "verbose_name": "Настройки почтового сервера",
                "verbose_name_plural": "Настройки почтового сервера",
            },
        ),
    ]










