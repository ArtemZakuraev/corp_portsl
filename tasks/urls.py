"""Tasks app URLs."""
from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.task_list, name='list'),
    path('<int:pk>/', views.task_detail, name='detail'),
    path('create/', views.create_task, name='create'),
    path('<int:pk>/edit/', views.edit_task, name='edit'),
    path('<int:pk>/update-status/', views.update_status, name='update_status'),
]
