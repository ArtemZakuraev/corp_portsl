"""Admin configuration for employees app."""
from django.contrib import admin
from .models import Employee, Department, Position


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'get_employee_count', 'created_at']
    list_filter = ['parent', 'created_at']
    search_fields = ['name', 'description']
    raw_id_fields = ['parent']
    
    def get_employee_count(self, obj):
        return obj.get_employee_count()
    get_employee_count.short_description = 'Кол-во сотрудников'


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'level', 'created_at']
    list_filter = ['department', 'level']
    search_fields = ['name']
    list_editable = ['level']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'position', 'supervisor', 'phone', 'is_active']
    list_filter = ['is_active', 'position__department', 'hire_date']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'phone']
    raw_id_fields = ['user', 'supervisor', 'position']
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'position', 'supervisor')
        }),
        ('Контактная информация', {
            'fields': ('phone', 'avatar')
        }),
        ('Даты', {
            'fields': ('hire_date', 'birth_date'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
