"""
Employees app views with optimized queries and modern Django patterns.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import Employee, Department, Position


@login_required
def dashboard(request):
    """Main dashboard view with organizational overview."""
    # Optimized query with select_related and prefetch_related
    departments = Department.objects.annotate(
        employee_count=Count('positions__employees', distinct=True)
    ).select_related('parent')[:10]
    
    recent_employees = Employee.objects.select_related(
        'user', 'position', 'position__department'
    ).filter(is_active=True).order_by('-created_at')[:5]
    
    context = {
        'departments': departments,
        'recent_employees': recent_employees,
        'total_employees': 0,  # Will be updated after checking table existence
        'total_departments': 0,  # Will be updated after checking table existence
    }
    
    # Try to get counts, handle case where tables don't exist yet
    try:
        context['total_employees'] = Employee.objects.filter(is_active=True).count()
    except Exception:
        context['total_employees'] = 0
        
    try:
        context['total_departments'] = Department.objects.count()
    except Exception:
        context['total_departments'] = 0
    
    return render(request, 'employees/dashboard.html', context)


@login_required
def employee_list(request):
    """Employee list with search, filtering, and pagination."""
    queryset = Employee.objects.select_related(
        'user', 'position', 'position__department', 'supervisor'
    ).filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(position__name__icontains=search_query)
        )
    
    # Filter by department
    department_id = request.GET.get('department')
    if department_id:
        queryset = queryset.filter(position__department_id=department_id)
    
    # Pagination
    paginator = Paginator(queryset, 20)
    page = request.GET.get('page')
    
    try:
        employees = paginator.page(page)
    except PageNotAnInteger:
        employees = paginator.page(1)
    except EmptyPage:
        employees = paginator.page(paginator.num_pages)
    
    departments = Department.objects.all()
    
    context = {
        'employees': employees,
        'departments': departments,
        'search_query': search_query,
        'selected_department': department_id,
    }
    return render(request, 'employees/employee_list.html', context)


@login_required
def employee_detail(request, pk):
    """Employee detail view with org chart data."""
    employee = get_object_or_404(
        Employee.objects.select_related(
            'user', 'position', 'position__department', 'supervisor'
        ).prefetch_related(
            'subordinates',
            'subordinates__user',
            'subordinates__position'
        ),
        pk=pk
    )
    
    context = {
        'employee': employee,
        'org_chart_data': employee.get_organization_chart_data(),
    }
    return render(request, 'employees/employee_detail.html', context)


@login_required
@require_http_methods(["GET"])
def organization_chart(request):
    """API endpoint for organization chart data."""
    # Get root employees (no supervisor)
    root_employees = Employee.objects.filter(
        supervisor__isnull=True,
        is_active=True
    ).select_related('position', 'position__department')
    
    chart_data = [e.get_organization_chart_data() for e in root_employees]
    
    return JsonResponse({'chart': chart_data})


@login_required
def department_structure(request, pk=None):
    """Department structure view."""
    if pk:
        department = get_object_or_404(
            Department.objects.prefetch_related(
                'children',
                'positions__employees__user'
            ),
            pk=pk
        )
    else:
        # Show root departments (no parent)
        department = None
        departments = Department.objects.filter(
            parent__isnull=True
        ).prefetch_related('children')
    
    context = {
        'department': department,
        'departments': departments if not pk else [],
    }
    return render(request, 'employees/department_structure.html', context)


def error_404(request, exception):
    """Custom 404 error handler."""
    return render(request, 'errors/404.html', status=404)


def error_500(request):
    """Custom 500 error handler."""
    return render(request, 'errors/500.html', status=500)
