# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0013_change_upload_to_portal"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="caldav_email",
            field=models.EmailField(
                blank=True,
                help_text="Email для подключения к серверу CalDAV. Используется для формирования URL календаря.",
                max_length=255,
                verbose_name="Email для CalDAV",
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="caldav_password",
            field=models.CharField(
                blank=True,
                help_text="Пароль для подключения к серверу CalDAV. Хранится в открытом виде.",
                max_length=255,
                verbose_name="Пароль CalDAV",
            ),
        ),
    ]


