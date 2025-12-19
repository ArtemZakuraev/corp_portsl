# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_userprofile_is_wiki_moderator'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='photo',
            field=models.ImageField(
                blank=True,
                help_text='Загрузите фото в формате JPG, PNG или GIF.',
                null=True,
                upload_to='portal/',
                verbose_name='Фотография'
            ),
        ),
    ]



