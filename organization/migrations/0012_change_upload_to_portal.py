# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0011_position_alter_department_head_alter_unit_head_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portalsettings',
            name='logo',
            field=models.ImageField(
                blank=True,
                help_text='Рекомендуется загружать изображение в формате PNG с прозрачным фоном.',
                null=True,
                upload_to='portal/',
                verbose_name='Логотип'
            ),
        ),
        migrations.AlterField(
            model_name='portalsettings',
            name='favicon',
            field=models.ImageField(
                blank=True,
                help_text='Иконка сайта (обычно квадратное изображение 32x32 или 64x64).',
                null=True,
                upload_to='portal/',
                verbose_name='Favicon'
            ),
        ),
        migrations.AlterField(
            model_name='departmenthead',
            name='photo',
            field=models.ImageField(
                blank=True,
                help_text='Загрузите фото в формате JPG, PNG или GIF.',
                null=True,
                upload_to='portal/',
                verbose_name='Фотография'
            ),
        ),
        migrations.AlterField(
            model_name='unithead',
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



