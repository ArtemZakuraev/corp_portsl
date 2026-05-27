"""Settings app URLs."""
from django.urls import path
from . import views

app_name = 'settings'

urlpatterns = [
    path('system/', views.system_settings, name='system'),
    path('mattermost-profile/', views.mattermost_profile_view, name='mattermost_profile'),
    path('mattermost-test/', views.test_mattermost_connection, name='mattermost_test'),
]
