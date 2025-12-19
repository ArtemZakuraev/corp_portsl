# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_userprofile_is_news_moderator'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='mattermost_username',
            field=models.CharField(blank=True, help_text='Логин для авторизации на сервере Mattermost.', max_length=255, verbose_name='Логин Mattermost'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mattermost_password',
            field=models.CharField(blank=True, help_text='Пароль для авторизации на сервере Mattermost. Хранится в открытом виде.', max_length=255, verbose_name='Пароль Mattermost'),
        ),
    ]






