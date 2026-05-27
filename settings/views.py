"""Settings app views - System configuration and user Mattermost profiles."""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.conf import settings as django_settings
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json

from .models import SystemSetting, MattermostProfile


@login_required
@user_passes_test(lambda u: u.is_staff)
def system_settings(request):
    """System settings page for administrators."""
    
    # Get current settings from database or environment
    site_url = SystemSetting.get_value('site_url', getattr(django_settings, 'SITE_URL', 'http://localhost:8000'))
    mattermost_url = SystemSetting.get_value('mattermost_url', getattr(django_settings, 'MATTERMOST_URL', ''))
    mattermost_api_url = SystemSetting.get_value('mattermost_api_url', getattr(django_settings, 'MATTERMOST_API_URL', ''))
    mattermost_verify_ssl = SystemSetting.get_value('mattermost_verify_ssl', 'True') == 'True'
    onlyoffice_url = SystemSetting.get_value('onlyoffice_url', getattr(django_settings, 'ONLYOFFICE_URL', 'http://onlyoffice:80'))
    debug_mode = SystemSetting.get_value('debug_mode', str(django_settings.DEBUG)) == 'True'
    background_image_url = SystemSetting.get_value('background_image_url', '')
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            # Save system settings
            SystemSetting.set_value('site_url', data.get('site_url', ''), 'URL сайта', request.user)
            SystemSetting.set_value('mattermost_url', data.get('mattermost_url', ''), 'URL Mattermost webhook', request.user)
            SystemSetting.set_value('mattermost_api_url', data.get('mattermost_api_url', ''), 'URL Mattermost API', request.user)
            SystemSetting.set_value('mattermost_verify_ssl', 'on' in data.get('mattermost_verify_ssl', ''), 'Проверка SSL сертификата Mattermost', request.user)
            SystemSetting.set_value('onlyoffice_url', data.get('onlyoffice_url', ''), 'URL OnlyOffice', request.user)
            SystemSetting.set_value('debug_mode', 'on' in data.get('debug_mode', ''), 'Режим отладки', request.user)
            SystemSetting.set_value('background_image_url', data.get('background_image_url', ''), 'URL фонового изображения', request.user)
            
            messages.success(request, 'Настройки системы успешно сохранены!')
        except Exception as e:
            messages.error(request, f'Ошибка сохранения настроек: {e}')
        
        return redirect('settings:system')
    
    context = {
        'site_url': site_url,
        'mattermost_url': mattermost_url,
        'mattermost_api_url': mattermost_api_url,
        'mattermost_verify_ssl': mattermost_verify_ssl,
        'onlyoffice_url': onlyoffice_url,
        'debug_mode': debug_mode,
        'background_image_url': background_image_url,
    }
    
    return render(request, 'settings/system_settings.html', context)


@login_required
def mattermost_profile_view(request):
    """User's personal Mattermost profile settings."""
    
    profile = MattermostProfile.get_user_profile(request.user)
    
    if request.method == 'POST':
        try:
            data = request.POST
            
            profile.mm_username = data.get('mm_username', '').strip()
            profile.mm_password = data.get('mm_password', '')  # Don't strip password
            profile.mm_token = data.get('mm_token', '').strip()
            profile.is_active = 'is_active' in data
            
            # Clear token if password is set and vice versa (optional logic)
            if profile.mm_password and profile.mm_token:
                # Keep both if user provided both, or implement mutual exclusion
                pass
            
            profile.save()
            messages.success(request, 'Настройки Mattermost успешно сохранены!')
        except Exception as e:
            messages.error(request, f'Ошибка сохранения профиля: {e}')
        
        return redirect('settings:mattermost_profile')
    
    context = {
        'profile': profile,
        'has_credentials': profile.has_credentials,
    }
    
    return render(request, 'settings/mattermost_profile.html', context)


@login_required
@require_http_methods(["POST"])
def test_mattermost_connection(request):
    """Test Mattermost connection with user's credentials."""
    from mattermost_integration.models import get_mattermost_client, MattermostConfig
    
    profile = MattermostProfile.get_user_profile(request.user)
    
    if not profile.has_credentials:
        return JsonResponse({
            'success': False,
            'error': 'Необходимо указать имя пользователя и пароль/токен'
        })
    
    # Create custom config with user credentials
    config = MattermostConfig(
        api_url=SystemSetting.get_value('mattermost_api_url', getattr(django_settings, 'MATTERMOST_API_URL', '')),
        token=profile.mm_token if profile.mm_token else None,
        verify_ssl=SystemSetting.get_value('mattermost_verify_ssl', 'True') == 'True',
    )
    
    # Test connection
    result = {
        'success': False,
        'error': None,
        'username': profile.mm_username,
    }
    
    try:
        import requests
        
        api_url = config.api_url.rstrip('/')
        verify_ssl = config.verify_ssl
        
        # Try to authenticate and get user info
        if profile.mm_token:
            # Use token authentication
            headers = {'Authorization': f'Bearer {profile.mm_token}'}
        else:
            # Use username/password authentication
            auth_data = {'login_id': profile.mm_username, 'password': profile.mm_password}
            login_response = requests.post(
                f'{api_url}/api/v4/users/login',
                json=auth_data,
                verify=verify_ssl,
                timeout=10
            )
            
            if login_response.status_code != 200:
                result['error'] = f'Ошибка аутентификации: HTTP {login_response.status_code}'
                return JsonResponse(result)
            
            # Extract token from response header
            token = login_response.headers.get('Token')
            if not token:
                result['error'] = 'Токен не получен от сервера'
                return JsonResponse(result)
            
            headers = {'Authorization': f'Bearer {token}'}
        
        # Get current user info to verify connection
        user_response = requests.get(
            f'{api_url}/api/v4/users/me',
            headers=headers,
            verify=verify_ssl,
            timeout=10
        )
        
        if user_response.status_code == 200:
            user_data = user_response.json()
            result['success'] = True
            result['mm_user_id'] = user_data.get('id')
            result['mm_username'] = user_data.get('username')
            result['message'] = f'Подключение успешно! Пользователь: {user_data.get("username")}'
        else:
            result['error'] = f'Ошибка получения данных пользователя: HTTP {user_response.status_code}'
    
    except requests.RequestException as e:
        result['error'] = f'Ошибка подключения: {str(e)}'
    except Exception as e:
        result['error'] = f'Неизвестная ошибка: {str(e)}'
    
    return JsonResponse(result)
