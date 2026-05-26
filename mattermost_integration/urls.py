"""Mattermost Integration app URLs - Modern interface."""
from django.urls import path
from . import views

app_name = 'mattermost'

urlpatterns = [
    # Dashboard - main interface
    path('', views.dashboard, name='dashboard'),
    
    # Send message interface
    path('send/', views.send_message, name='send'),
    
    # Message log with filtering
    path('log/', views.message_log, name='log'),
    
    # Test connection
    path('test/', views.test_connection, name='test'),
    
    # Webhook endpoint for receiving messages from Mattermost
    path('webhook/', views.mattermost_webhook, name='webhook'),
]
