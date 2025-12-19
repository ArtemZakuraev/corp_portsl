from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="task",
            name="reminder_sent",
            field=models.BooleanField(
                default=False,
                help_text="Отмечается после отправки email-напоминания по сроку задачи.",
                verbose_name="Напоминание отправлено",
            ),
        ),
    ]









