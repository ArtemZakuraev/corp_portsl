# Generated manually

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0007_department_parent_department'),
    ]

    operations = [
        migrations.CreateModel(
            name='DepartmentHead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Фамилия')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=150, verbose_name='Отчество')),
                ('department', models.CharField(blank=True, max_length=255, verbose_name='Департамент')),
                ('unit', models.CharField(blank=True, max_length=255, verbose_name='Отдел')),
                ('position', models.CharField(blank=True, max_length=255, verbose_name='Должность')),
                ('phone_personal', models.CharField(blank=True, max_length=50, verbose_name='Личный телефон')),
                ('phone_internal', models.CharField(blank=True, max_length=20, verbose_name='Внутренний телефон')),
                ('photo', models.ImageField(blank=True, help_text='Загрузите фото в формате JPG, PNG или GIF.', null=True, upload_to='employees/photos/', verbose_name='Фотография')),
                ('department_name', models.CharField(help_text='Название департамента, которым руководит данный сотрудник.', max_length=255, verbose_name='Наименование департамента')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='department_heads', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'Руководитель департамента',
                'verbose_name_plural': 'Руководители департаментов',
                'unique_together': {('user', 'department_name')},
            },
        ),
        migrations.CreateModel(
            name='UnitHead',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='Фамилия')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='Имя')),
                ('middle_name', models.CharField(blank=True, max_length=150, verbose_name='Отчество')),
                ('department', models.CharField(blank=True, max_length=255, verbose_name='Департамент')),
                ('unit', models.CharField(blank=True, max_length=255, verbose_name='Отдел')),
                ('position', models.CharField(blank=True, max_length=255, verbose_name='Должность')),
                ('phone_personal', models.CharField(blank=True, max_length=50, verbose_name='Личный телефон')),
                ('phone_internal', models.CharField(blank=True, max_length=20, verbose_name='Внутренний телефон')),
                ('photo', models.ImageField(blank=True, help_text='Загрузите фото в формате JPG, PNG или GIF.', null=True, upload_to='employees/photos/', verbose_name='Фотография')),
                ('unit_name', models.CharField(help_text='Название отдела, которым руководит данный сотрудник.', max_length=255, verbose_name='Наименование отдела')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='unit_heads', to=settings.AUTH_USER_MODEL, verbose_name='Сотрудник')),
            ],
            options={
                'verbose_name': 'Руководитель отдела',
                'verbose_name_plural': 'Руководители отделов',
                'unique_together': {('user', 'unit_name')},
            },
        ),
        migrations.AddField(
            model_name='department',
            name='department_head',
            field=models.ForeignKey(blank=True, help_text='Выберите руководителя из таблицы руководителей департаментов.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='departments', to='organization.departmenthead', verbose_name='Руководитель департамента (из таблицы)'),
        ),
        migrations.AddField(
            model_name='unit',
            name='unit_head',
            field=models.ForeignKey(blank=True, help_text='Выберите руководителя из таблицы руководителей отделов.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='units', to='organization.unithead', verbose_name='Руководитель отдела (из таблицы)'),
        ),
    ]






