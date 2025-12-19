# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0008_departmenthead_unithead'),
    ]

    operations = [
        migrations.CreateModel(
            name='MattermostSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('server_url', models.URLField(help_text='Например: https://mattermost.example.com', verbose_name='URL сервера Mattermost')),
                ('api_version', models.CharField(default='v4', help_text='Версия Mattermost API (обычно v4).', max_length=20, verbose_name='Версия API')),
            ],
            options={
                'verbose_name': 'Настройки Mattermost',
                'verbose_name_plural': 'Настройки Mattermost',
            },
        ),
    ]






