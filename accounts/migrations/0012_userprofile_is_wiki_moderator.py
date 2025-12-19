# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_userprofile_menu_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_wiki_moderator',
            field=models.BooleanField(default=False, help_text='Если отмечено, пользователь может создавать и редактировать статьи базы знаний.', verbose_name='Модератор базы знаний'),
        ),
    ]




