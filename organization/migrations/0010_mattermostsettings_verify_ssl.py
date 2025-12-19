# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0009_mattermostsettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='mattermostsettings',
            name='verify_ssl',
            field=models.BooleanField(default=True, help_text='Отключите, если используется самоподписанный сертификат. Не рекомендуется для production.', verbose_name='Проверять SSL сертификат'),
        ),
    ]






