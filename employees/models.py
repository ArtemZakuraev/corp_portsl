"""
Employees app models - Organizational structure and employee management.
Optimized with proper indexing, relationships, and modern Django features.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, RegexValidator


class Department(models.Model):
    """Department model for organizational structure."""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_('Название отдела')
    )
    description = models.TextField(
        blank=True,
        verbose_name=_('Описание')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('Родительский отдел')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Отдел')
        verbose_name_plural = _('Отделы')
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['parent']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_all_descendants(self):
        """Get all descendant departments recursively."""
        descendants = list(self.children.all())
        for child in self.children.all():
            descendants.extend(child.get_all_descendants())
        return descendants
    
    def get_employee_count(self):
        """Get total number of employees in this department and subdepartments."""
        count = self.employee_set.count()
        for child in self.children.all():
            count += child.get_employee_count()
        return count


class Position(models.Model):
    """Position/Job title model."""
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name=_('Название должности')
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_('Отдел')
    )
    level = models.PositiveIntegerField(
        default=1,
        help_text=_('Уровень должности в иерархии (1-10)')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['department', 'level', 'name']
        verbose_name = _('Должность')
        verbose_name_plural = _('Должности')
        indexes = [
            models.Index(fields=['department', 'level']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Employee(models.Model):
    """Employee model with comprehensive information."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        verbose_name=_('Пользователь')
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        related_name='employees',
        verbose_name=_('Должность')
    )
    supervisor = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_('Руководитель')
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r'^[\d\+\-\(\)\s]+$', _('Введите корректный номер телефона'))],
        verbose_name=_('Телефон')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name=_('Аватар')
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата приема на работу')
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_('Дата рождения')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активен')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['user__last_name', 'user__first_name']
        verbose_name = _('Сотрудник')
        verbose_name_plural = _('Сотрудники')
        indexes = [
            models.Index(fields=['user__last_name', 'user__first_name']),
            models.Index(fields=['position']),
            models.Index(fields=['supervisor']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.get_full_name()
    
    def get_full_name(self):
        """Get employee's full name."""
        return f"{self.user.last_name} {self.user.first_name}"
    
    def get_department(self):
        """Get employee's department."""
        return self.position.department if self.position else None
    
    def get_subordinates_recursive(self):
        """Get all subordinates recursively."""
        subordinates = list(self.subordinates.all())
        for sub in self.subordinates.all():
            subordinates.extend(sub.get_subordinates_recursive())
        return subordinates
    
    def get_organization_chart_data(self):
        """Get data for organization chart visualization."""
        return {
            'id': self.id,
            'name': self.get_full_name(),
            'position': str(self.position) if self.position else '',
            'department': str(self.get_department()),
            'children': [s.get_organization_chart_data() for s in self.subordinates.all()]
        }
