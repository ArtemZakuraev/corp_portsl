"""Settings app views - System configuration."""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings as django_settings


@login_required
@user_passes_test(lambda u: u.is_staff)
def system_settings(request):
    """System settings page."""
    context = {
        'debug_mode': django_settings.DEBUG,
        'site_url': getattr(django_settings, 'SITE_URL', 'http://localhost:8000'),
        'email_host': getattr(django_settings, 'EMAIL_HOST', 'Not configured'),
        'mattermost_url': getattr(django_settings, 'MATTERMOST_URL', 'Not configured'),
        'onlyoffice_url': getattr(django_settings, 'ONLYOFFICE_URL', 'http://onlyoffice:80'),
    }
    
    if request.method == 'POST':
        messages.success(request, 'Настройки сохранены (демо-режим)')
        return redirect('settings:system')
    
    return render(request, 'settings/system_settings.html', context)
