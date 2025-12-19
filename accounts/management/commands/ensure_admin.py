import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает администратора при старте, если он еще не создан."

    def handle(self, *args, **options):
        User = get_user_model()

        # Если в базе уже есть суперюзер, ничего не делаем
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS("Суперпользователь уже существует."))
            return

        username = os.getenv("ADMIN_USERNAME")
        password = os.getenv("ADMIN_PASSWORD")
        email = os.getenv("ADMIN_EMAIL", "")

        # Если переменные окружения не заданы — предполагаем,
        # что данные уже будут в базе (например, из дампа) и выходим.
        if not username or not password:
            self.stdout.write(
                self.style.WARNING(
                    "ADMIN_USERNAME/ADMIN_PASSWORD не заданы, суперпользователь не создан."
                )
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )

        # is_staff/is_superuser = True автоматически для create_superuser,
        # их можно использовать как флаг \"администратор\".
        self.stdout.write(
            self.style.SUCCESS(
                f"Создан суперпользователь '{username}' (администратор портала)."
            )
        )










