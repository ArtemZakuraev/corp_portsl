"""
URL configuration for corp_portal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Apps
    path('', RedirectView.as_view(url='/dashboard/', permanent=False), name='home'),
    path('dashboard/', include('employees.urls')),
    path('news/', include('news.urls')),
    path('tasks/', include('tasks.urls')),
    path('wiki/', include('wiki.urls')),
    path('meetings/', include('meetings.urls')),
    path('mattermost/', include('mattermost_integration.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error pages
handler404 = 'employees.views.error_404'
handler500 = 'employees.views.error_500'
