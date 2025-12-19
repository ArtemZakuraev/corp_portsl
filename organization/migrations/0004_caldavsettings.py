from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0003_vacationrequest_vacationperiod"),
    ]

    operations = [
        migrations.CreateModel(
            name="CaldavSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "server_url",
                    models.URLField(
                        help_text="Например: https://caldav.example.com/calendars/",
                        verbose_name="URL CalDAV сервера",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        blank=True,
                        help_text="Опционально. Можно оставить пустым, если используется авторизация по учетным данным сотрудников.",
                        max_length=255,
                        verbose_name="Имя пользователя (по умолчанию)",
                    ),
                ),
                (
                    "password",
                    models.CharField(
                        blank=True,
                        help_text="Опционально. Хранится в базе в открытом виде, используйте отдельную учетную запись с ограниченными правами.",
                        max_length=255,
                        verbose_name="Пароль (по умолчанию)",
                    ),
                ),
            ],
            options={
                "verbose_name": "Настройки CalDAV",
                "verbose_name_plural": "Настройки CalDAV",
            },
        ),
    ]









