"""
Утилиты для работы с задачами.
"""
from django.contrib.auth import get_user_model
from organization.models import Department, Unit

User = get_user_model()


def get_user_subordinates(user):
    """
    Возвращает список подчиненных пользователя.
    Подчиненные - это сотрудники отделов и департаментов, которыми руководит пользователь.
    
    Args:
        user: Пользователь, для которого нужно получить подчиненных
        
    Returns:
        QuerySet пользователей, которые являются подчиненными
    """
    from django.db.models import Q
    
    # Получаем всех подчиненных
    subordinates_ids = set()
    
    # 1. Получаем департаменты, которыми руководит пользователь
    departments = Department.objects.filter(
        Q(head=user) | Q(department_head__user=user)
    )
    
    # Сотрудники из департаментов (через UserProfile)
    for dept in departments:
        # Сотрудники, у которых департамент = dept (через UserProfile)
        dept_employees = User.objects.filter(profile__department=dept).exclude(id=user.id).values_list('id', flat=True)
        subordinates_ids.update(dept_employees)
        
        # Также получаем сотрудников из всех отделов, входящих в этот департамент
        for unit in dept.units.all():
            # Через UserProfile
            unit_employees_profile = User.objects.filter(profile__unit=unit).exclude(id=user.id).values_list('id', flat=True)
            subordinates_ids.update(unit_employees_profile)
            # Через ManyToMany связь employees
            unit_employees_m2m = unit.employees.exclude(id=user.id).values_list('id', flat=True)
            subordinates_ids.update(unit_employees_m2m)
    
    # 2. Получаем отделы, которыми руководит пользователь (независимо от департамента)
    units = Unit.objects.filter(
        Q(head=user) | Q(unit_head__user=user)
    )
    
    # Сотрудники из отделов (через UserProfile и ManyToMany)
    for unit in units:
        # Через UserProfile
        unit_employees_profile = User.objects.filter(profile__unit=unit).exclude(id=user.id).values_list('id', flat=True)
        subordinates_ids.update(unit_employees_profile)
        # Через ManyToMany связь employees
        unit_employees_m2m = unit.employees.exclude(id=user.id).values_list('id', flat=True)
        subordinates_ids.update(unit_employees_m2m)
    
    # Возвращаем QuerySet пользователей
    if subordinates_ids:
        return User.objects.filter(id__in=subordinates_ids).distinct()
    else:
        return User.objects.none()


def has_subordinates(user):
    """
    Проверяет, есть ли у пользователя подчиненные.
    
    Args:
        user: Пользователь для проверки
        
    Returns:
        bool: True, если у пользователя есть подчиненные
    """
    return get_user_subordinates(user).exists()

