from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("organization", "0002_mailserversettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="VacationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("department", models.CharField(max_length=255, verbose_name="Департамент")),
                ("unit", models.CharField(max_length=255, verbose_name="Отдел")),
                ("position", models.CharField(max_length=255, verbose_name="Должность")),
                ("last_name", models.CharField(max_length=150, verbose_name="Фамилия")),
                ("first_name", models.CharField(max_length=150, verbose_name="Имя")),
                ("middle_name", models.CharField(max_length=150, verbose_name="Отчество")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="vacation_requests",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "График отпусков (заявка)",
                "verbose_name_plural": "Графики отпусков (заявки)",
            },
        ),
        migrations.CreateModel(
            name="VacationPeriod",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("start_date", models.DateField(verbose_name="Дата начала")),
                ("end_date", models.DateField(verbose_name="Дата окончания")),
                (
                    "vacation_type",
                    models.CharField(
                        choices=[("main", "Основной отпуск"), ("extra", "Дополнительный отпуск")],
                        default="main",
                        max_length=20,
                        verbose_name="Тип отпуска",
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="periods",
                        to="organization.vacationrequest",
                        verbose_name="График отпусков",
                    ),
                ),
            ],
            options={
                "verbose_name": "Период отпуска",
                "verbose_name_plural": "Периоды отпусков",
            },
        ),
    ]










