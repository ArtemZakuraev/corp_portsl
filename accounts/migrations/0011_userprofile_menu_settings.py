# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_userprofile_sidebar_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='menu_items_settings',
            field=models.JSONField(blank=True, default=dict, help_text='JSON с настройками пунктов меню: порядок, видимость, избранное.', verbose_name='Настройки пунктов меню'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='menu_show_favorites_only',
            field=models.BooleanField(default=False, help_text='Если включено, в меню отображаются только избранные пункты.', verbose_name='Показывать только избранное'),
        ),
    ]





