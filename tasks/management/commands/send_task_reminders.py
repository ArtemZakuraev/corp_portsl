from datetime import date

from django.conf import settings
from django.core.mail import send_mail
from django.core.management.base import BaseCommand

from tasks.models import Task


class Command(BaseCommand):
    help = "Отправляет email-напоминания по задачам с наступившим сроком выполнения."

    def handle(self, *args, **options):
        today = date.today()
        qs = Task.objects.filter(
            due_date=today,
            reminder_sent=False,
        ).exclude(assignee_email="")

        count = 0
        for task in qs:
            subject = f"Напоминание о задаче: {task.title}"
            message = (
                f"Сегодня срок выполнения задачи:\n\n"
                f"{task.title}\n\n"
                f"{task.description}\n\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assignee_email],
                fail_silently=True,
            )
            task.reminder_sent = True
            task.save(update_fields=["reminder_sent"])
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Отправлено напоминаний: {count}"))









