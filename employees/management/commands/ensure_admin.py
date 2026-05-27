import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employees.models import Employee


class Command(BaseCommand):
    help = 'Создает или обновляет учетную запись администратора и профиль сотрудника'

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USERNAME', 'admin')
        password = os.getenv('ADMIN_PASSWORD', 'adminpassword')
        email = os.getenv('ADMIN_EMAIL', 'admin@example.com')

        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            # Проверяем, нужно ли обновить пароль или email
            updated = False
            if user.email != email:
                user.email = email
                updated = True
            # Обновляем пароль только если он не совпадает (хеши не сравниваются напрямую)
            # Поэтому просто устанавливаем новый пароль при каждом запуске для гарантии
            user.set_password(password)
            updated = True
            
            if updated:
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Учетная запись администратора "{username}" обновлена.'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Учетная запись администратора "{username}" уже существует и актуальна.'))
        else:
            user = User.objects.create_superuser(
                username=username,
                password=password,
                email=email,
                first_name='Admin',
                last_name='User'
            )
            self.stdout.write(self.style.SUCCESS(f'Администратор "{username}" успешно создан.'))
        
        # Создаем профиль сотрудника для администратора, если он не существует
        if not hasattr(user, 'employee_profile'):
            Employee.objects.create(
                user=user,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Профиль сотрудника для администратора "{username}" создан.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Профиль сотрудника для администратора "{username}" уже существует.'))
