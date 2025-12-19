# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("organization", "0012_change_upload_to_portal"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="caldavsettings",
            name="username",
        ),
        migrations.RemoveField(
            model_name="caldavsettings",
            name="password",
        ),
        migrations.AlterField(
            model_name="caldavsettings",
            name="server_url",
            field=models.URLField(
                help_text="Базовый URL сервера CalDAV (например: https://caldav.example.com). Email и пароль настраиваются в профиле пользователя.",
                verbose_name="URL CalDAV сервера",
            ),
        ),
    ]

