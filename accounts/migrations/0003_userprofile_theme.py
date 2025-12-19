from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_userprofile"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="theme_mode",
            field=models.CharField(
                choices=[
                    ("default", "Стиль системы по умолчанию"),
                    ("light", "Светлая тема"),
                    ("dark", "Тёмная тема"),
                    ("custom", "Пользовательские цвета"),
                ],
                default="default",
                max_length=20,
                verbose_name="Режим темы",
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="theme_primary_color",
            field=models.CharField(
                blank=True,
                help_text='HEX, например #ffd94a. Используется при режиме "Пользовательские цвета".',
                max_length=7,
                verbose_name="Основной цвет акцента",
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="theme_sidebar_bg_color",
            field=models.CharField(
                blank=True,
                help_text="HEX-цвет фона бокового меню.",
                max_length=7,
                verbose_name="Цвет фона меню",
            ),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="theme_header_bg_color",
            field=models.CharField(
                blank=True,
                help_text="HEX-цвет фона верхней панели.",
                max_length=7,
                verbose_name="Цвет шапки",
            ),
        ),
    ]









