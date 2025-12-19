# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_userprofile_dashboard_blocks_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='task_priority_important_color',
            field=models.CharField(default='#4CAF50', help_text="HEX-цвет для задач с важностью 'Важно' (по умолчанию: #4CAF50).", max_length=7, verbose_name='Цвет для важных задач'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='task_priority_urgent_color',
            field=models.CharField(default='#FF9800', help_text="HEX-цвет для задач с важностью 'Срочно' (по умолчанию: #FF9800).", max_length=7, verbose_name='Цвет для срочных задач'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='task_priority_critical_color',
            field=models.CharField(default='#F44336', help_text="HEX-цвет для задач с важностью 'Критично' (по умолчанию: #F44336).", max_length=7, verbose_name='Цвет для критичных задач'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='task_view_mode',
            field=models.CharField(choices=[('list', 'Список'), ('kanban', 'Канбан-доска')], default='list', help_text='Выберите способ отображения списка задач.', max_length=20, verbose_name='Режим отображения задач'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='task_sort_by',
            field=models.CharField(choices=[('priority', 'По важности'), ('due_date', 'По дате окончания'), ('created_at', 'По дате создания')], default='due_date', help_text='Выберите способ сортировки задач.', max_length=20, verbose_name='Сортировка задач'),
        ),
    ]





