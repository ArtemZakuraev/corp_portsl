# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='WikiArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Краткое название статьи, которое будет отображаться в содержании.', max_length=255, verbose_name='Название статьи')),
                ('slug', models.SlugField(help_text='Уникальный идентификатор для URL статьи (например: \'nastroyka-sistemy\').', max_length=255, unique=True, verbose_name='URL-адрес')),
                ('content', models.TextField(help_text='Основной текст статьи. Поддерживается HTML-разметка для форматирования.', verbose_name='Содержание статьи')),
                ('order', models.PositiveIntegerField(default=0, help_text='Число для сортировки статей в содержании (меньше = выше в списке).', verbose_name='Порядок отображения')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('is_published', models.BooleanField(default=True, help_text='Если снято, статья не будет отображаться в содержании.', verbose_name='Опубликовано')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wiki_articles', to=settings.AUTH_USER_MODEL, verbose_name='Автор')),
                ('parent', models.ForeignKey(blank=True, help_text='Выберите родительскую статью, если эта статья является подразделом другой статьи.', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='wiki.wikiarticle', verbose_name='Родительская статья')),
            ],
            options={
                'verbose_name': 'Статья базы знаний',
                'verbose_name_plural': 'Статьи базы знаний',
                'ordering': ['order', 'title'],
            },
        ),
        migrations.CreateModel(
            name='WikiImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(help_text='Загрузите изображение в формате JPG, PNG, GIF или WebP.', upload_to='wiki/images/', verbose_name='Изображение')),
                ('alt_text', models.CharField(blank=True, help_text='Описание изображения для доступности (alt-текст).', max_length=255, verbose_name='Альтернативный текст')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='wiki.wikiarticle', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Изображение статьи',
                'verbose_name_plural': 'Изображения статей',
                'ordering': ['uploaded_at'],
            },
        ),
        migrations.CreateModel(
            name='WikiFile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(help_text='Загрузите файл для прикрепления к статье.', upload_to='wiki/files/', verbose_name='Файл')),
                ('name', models.CharField(blank=True, help_text='Отображаемое название файла (по умолчанию используется имя файла).', max_length=255, verbose_name='Название файла')),
                ('description', models.TextField(blank=True, help_text='Краткое описание файла.', verbose_name='Описание')),
                ('uploaded_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='wiki.wikiarticle', verbose_name='Статья')),
            ],
            options={
                'verbose_name': 'Файл статьи',
                'verbose_name_plural': 'Файлы статей',
                'ordering': ['uploaded_at'],
            },
        ),
        migrations.AddIndex(
            model_name='wikiarticle',
            index=models.Index(fields=['slug'], name='wiki_wikiar_slug_idx'),
        ),
        migrations.AddIndex(
            model_name='wikiarticle',
            index=models.Index(fields=['parent', 'order'], name='wiki_wikiar_parent__idx'),
        ),
    ]




