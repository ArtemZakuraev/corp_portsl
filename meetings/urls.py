"""Meetings app URLs."""
from django.urls import path
from . import views

app_name = 'meetings'

urlpatterns = [
    path('', views.meeting_list, name='list'),
    path('<int:pk>/', views.meeting_detail, name='detail'),
    path('create/', views.create_meeting, name='create'),
    path('<int:pk>/edit/', views.edit_meeting, name='edit'),
    path('<int:pk>/rsvp/', views.rsvp, name='rsvp'),
    path('<int:pk>/update-status/', views.update_status, name='update_status'),
]
