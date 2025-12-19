from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="PortalSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "site_name",
                    models.CharField(
                        default="Корпоративный портал",
                        max_length=255,
                        verbose_name="Название портала",
                    ),
                ),
                (
                    "logo",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="branding/",
                        verbose_name="Логотип",
                        help_text="Рекомендуется загружать изображение в формате PNG с прозрачным фоном.",
                    ),
                ),
                (
                    "favicon",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="branding/",
                        verbose_name="Favicon",
                        help_text="Иконка сайта (обычно квадратное изображение 32x32 или 64x64).",
                    ),
                ),
            ],
            options={
                "verbose_name": "Настройки портала",
                "verbose_name_plural": "Настройки портала",
            },
        ),
    ]










