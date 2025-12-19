# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_userprofile_task_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='sidebar_custom_enabled',
            field=models.BooleanField(default=False, help_text='Включите, чтобы настроить ширину и высоту левого меню под свой экран.', verbose_name='Включить настройку сайдбара'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sidebar_width',
            field=models.PositiveIntegerField(default=280, help_text='Ширина левого меню в пикселях (по умолчанию: 280px).', verbose_name='Ширина сайдбара (px)'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='sidebar_height',
            field=models.CharField(default='calc(100vh - 64px)', help_text='Высота левого меню. Можно указать в пикселях (например: 600px) или использовать calc (например: calc(100vh - 64px)).', max_length=50, verbose_name='Высота сайдбара'),
        ),
    ]





