"""Mattermost Integration app URLs - Telegram-style chat interface."""
from django.urls import path
from . import views

app_name = 'mattermost_integration'

urlpatterns = [
    # Main chat interface (Telegram-style)
    path('', views.chat_view, name='chat'),
    
    # API endpoints
    path('api/channels/', views.api_get_channels, name='api_get_channels'),
    path('api/messages/', views.api_get_messages, name='api_get_messages'),
    path('api/send/', views.api_send_message, name='api_send_message'),
    
    # Test connection
    path('test/', views.test_connection, name='test'),
]
