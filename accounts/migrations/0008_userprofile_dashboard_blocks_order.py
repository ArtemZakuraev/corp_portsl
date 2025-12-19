# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_alter_userprofile_department_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='dashboard_blocks_order',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='JSON-массив с идентификаторами блоков в порядке их отображения.',
                verbose_name='Порядок блоков на ленте',
            ),
        ),
    ]






