"""URL configuration for employees app."""
from django.urls import path
from . import views

app_name = 'employees'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('api/org-chart/', views.organization_chart, name='organization_chart'),
    path('departments/', views.department_structure, name='department_structure'),
    path('departments/<int:pk>/', views.department_structure, name='department_detail'),
    path('profile/', views.profile, name='profile'),
]
