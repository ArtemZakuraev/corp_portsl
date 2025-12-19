# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_task_reminder_sent'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='priority',
            field=models.CharField(blank=True, choices=[('important', 'Важно'), ('urgent', 'Срочно'), ('critical', 'Критично')], help_text='Выберите уровень важности задачи.', max_length=20, null=True, verbose_name='Важность'),
        ),
    ]





