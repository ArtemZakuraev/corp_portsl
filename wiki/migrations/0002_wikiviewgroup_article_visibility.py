# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wiki', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiViewGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Уникальное название группы просмотра.', max_length=255, unique=True, verbose_name='Название группы')),
                ('description', models.TextField(blank=True, help_text='Описание группы и её назначения.', verbose_name='Описание')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('users', models.ManyToManyField(blank=True, related_name='wiki_view_groups', to=settings.AUTH_USER_MODEL, verbose_name='Пользователи')),
            ],
            options={
                'verbose_name': 'Группа просмотра',
                'verbose_name_plural': 'Группы просмотра',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='wikiarticle',
            name='slug',
            field=models.SlugField(editable=False, help_text='Уникальный идентификатор для URL статьи (генерируется автоматически).', max_length=255, unique=True, verbose_name='URL-адрес'),
        ),
        migrations.AddField(
            model_name='wikiarticle',
            name='visibility_type',
            field=models.CharField(choices=[('all', 'Все (включая неавторизованных)'), ('registered', 'Только зарегистрированные пользователи'), ('groups', 'Пользователи групп')], default='registered', help_text='Выберите, кто имеет доступ к просмотру этой статьи.', max_length=20, verbose_name='Кто может видеть статью'),
        ),
        migrations.AddField(
            model_name='wikiarticle',
            name='view_groups',
            field=models.ManyToManyField(blank=True, related_name='articles', to='wiki.wikiviewgroup', verbose_name='Группы просмотра'),
        ),
    ]




