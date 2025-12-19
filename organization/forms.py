from django import forms
from django.db import connection

from .models import (
    CaldavSettings,
    Department,
    DepartmentHead,
    MailServerSettings,
    MattermostSettings,
    PortalSettings,
    Unit,
    UnitHead,
)


def _table_exists(table_name):
    """Проверяет, существует ли таблица в базе данных."""
    try:
        with connection.cursor() as cursor:
            # Для PostgreSQL проверяем в схеме public
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                )
                """,
                [table_name]
            )
            return cursor.fetchone()[0]
    except Exception:
        # В случае любой ошибки считаем, что таблица не существует
        return False


class PortalSettingsForm(forms.ModelForm):
    class Meta:
        model = PortalSettings
        fields = [
            "site_name",
            "logo",
            "favicon",
            "document_storage_type",
            "s3_endpoint_url",
            "s3_access_key",
            "s3_secret_key",
            "s3_bucket_name",
        ]
        widgets = {
            "s3_secret_key": forms.PasswordInput(render_value=True),
        }


class MailServerSettingsForm(forms.ModelForm):
    class Meta:
        model = MailServerSettings
        fields = ["host", "port", "use_tls", "use_ssl", "username", "password", "from_email"]
        widgets = {
            "password": forms.PasswordInput(render_value=True),
        }


class CaldavSettingsForm(forms.ModelForm):
    class Meta:
        model = CaldavSettings
        fields = ["server_url"]


class MattermostSettingsForm(forms.ModelForm):
    class Meta:
        model = MattermostSettings
        fields = ["server_url", "api_version", "verify_ssl"]


class DepartmentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Исключаем текущий департамент и все его поддепартаменты из списка возможных родительских департаментов
        # чтобы избежать циклических зависимостей
        if self.instance and self.instance.pk:
            exclude_ids = [self.instance.pk]
            # Рекурсивно собираем все поддепартаменты
            def get_sub_department_ids(dept):
                ids = [dept.pk]
                for sub_dept in dept.sub_departments.all():
                    ids.extend(get_sub_department_ids(sub_dept))
                return ids
            exclude_ids.extend(get_sub_department_ids(self.instance))
            self.fields["parent_department"].queryset = Department.objects.exclude(id__in=exclude_ids)
        else:
            self.fields["parent_department"].queryset = Department.objects.all()
        
        # Показываем всех руководителей департаментов
        # Проверяем, существует ли таблица перед установкой queryset
        if _table_exists("organization_departmenthead"):
            try:
                # Показываем всех руководителей департаментов
                self.fields["department_head"].queryset = DepartmentHead.objects.all().select_related('user')
            except Exception:
                # Если произошла ошибка, используем пустой queryset
                self.fields["department_head"].queryset = DepartmentHead.objects.none()
        else:
            # Если таблица еще не создана, используем пустой queryset
            self.fields["department_head"].queryset = DepartmentHead.objects.none()
        
        # Если есть выбранный department_head, устанавливаем его как начальное значение
        if (self.instance and self.instance.pk and 
            _table_exists("organization_departmenthead") and
            hasattr(self.instance, 'department_head') and 
            self.instance.department_head):
            try:
                self.fields["department_head"].initial = self.instance.department_head
            except Exception:
                pass

    class Meta:
        model = Department
        fields = ["name", "department_head", "parent_department", "units"]
        widgets = {
            "units": forms.SelectMultiple(attrs={"size": 10}),
        }


class UnitForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Показываем всех руководителей отделов
        # Проверяем, существует ли таблица перед установкой queryset
        if _table_exists("organization_unithead"):
            try:
                # Показываем всех руководителей отделов
                self.fields["unit_head"].queryset = UnitHead.objects.all().select_related('user')
            except Exception:
                # Если произошла ошибка, используем пустой queryset
                self.fields["unit_head"].queryset = UnitHead.objects.none()
        else:
            # Если таблица еще не создана, используем пустой queryset
            self.fields["unit_head"].queryset = UnitHead.objects.none()
        
        # Если есть выбранный unit_head, устанавливаем его как начальное значение
        if (self.instance and self.instance.pk and 
            _table_exists("organization_unithead") and
            hasattr(self.instance, 'unit_head') and 
            self.instance.unit_head):
            try:
                self.fields["unit_head"].initial = self.instance.unit_head
            except Exception:
                pass

    class Meta:
        model = Unit
        fields = ["name", "unit_head", "employees"]
        widgets = {
            "employees": forms.SelectMultiple(attrs={"size": 10}),
        }