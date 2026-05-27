"""Mattermost Integration app views - Telegram-style chat interface."""
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.cache import never_cache
import json
import logging
import requests
from datetime import datetime

from .models import MattermostMessage, MattermostConfig
from settings.models import SystemSetting, MattermostProfile

logger = logging.getLogger(__name__)


def _get_user_mm_credentials(user):
    """Get user's Mattermost credentials or system bot token."""
    try:
        profile = MattermostProfile.objects.get(user=user, is_active=True)
        if profile.has_credentials:
            return {
                'username': profile.mm_username,
                'password': profile.mm_password,
                'token': profile.mm_token,
                'is_personal': True
            }
    except MattermostProfile.DoesNotExist:
        pass
    
    # Fallback to system bot token
    bot_token = SystemSetting.get_mattermost_bot_token()
    if bot_token:
        return {
            'token': bot_token,
            'is_personal': False
        }
    
    return None


def _make_mm_request(endpoint, data=None, method='POST', user=None):
    """Make request to Mattermost API with user credentials."""
    mm_url = SystemSetting.get_mattermost_url()
    if not mm_url:
        return {'success': False, 'error': 'Mattermost URL не настроен'}
    
    creds = _get_user_mm_credentials(user) if user else None
    if not creds:
        return {'success': False, 'error': 'Нет учетных данных Mattermost'}
    
    verify_ssl = SystemSetting.is_ssl_verification_enabled()
    
    headers = {
        'Content-Type': 'application/json',
    }
    
    # Use token authentication
    if creds.get('token'):
        headers['Authorization'] = f"Bearer {creds['token']}"
    
    url = f"{mm_url.rstrip('/')}/api/v4{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, verify=verify_ssl, timeout=10)
        else:
            response = requests.post(
                url, 
                headers=headers, 
                json=data,
                verify=verify_ssl, 
                timeout=10
            )
        
        if response.status_code in [200, 201]:
            return {'success': True, 'data': response.json()}
        else:
            return {
                'success': False, 
                'error': f"HTTP {response.status_code}: {response.text}"
            }
    except requests.exceptions.SSLError as e:
        return {'success': False, 'error': f"SSL ошибка: {str(e)}"}
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f"Ошибка соединения: {str(e)}"}
    except Exception as e:
        return {'success': False, 'error': str(e)}


@login_required
@never_cache
def chat_view(request):
    """Main Telegram-style chat interface."""
    mm_url = SystemSetting.get_mattermost_url()
    
    if not mm_url:
        messages.warning(request, 'Адрес сервера Mattermost не настроен в системных настройках')
        return redirect('settings:mattermost_profile')
    
    creds = _get_user_mm_credentials(request.user)
    if not creds:
        messages.warning(request, 'Настройте учетные данные Mattermost в вашем профиле')
        return redirect('employees:profile')
    
    context = {
        'mm_url': mm_url.rstrip('/'),
        'user_credentials': creds,
        'is_personal': creds.get('is_personal', False),
    }
    
    return render(request, 'mattermost_integration/chat.html', context)


@login_required
@require_http_methods(["POST"])
def api_get_channels(request):
    """Get user's channels from Mattermost."""
    result = _make_mm_request('/channels/team/name/town-square', method='GET', user=request.user)
    
    if result['success']:
        # Get all channels user is member of
        teams_result = _make_mm_request('/teams', method='GET', user=request.user)
        if teams_result['success']:
            teams = teams_result['data']
            channels = []
            for team in teams:
                channels_result = _make_mm_request(f"/users/me/teams/{team['id']}/channels", method='GET', user=request.user)
                if channels_result['success']:
                    channels.extend(channels_result['data'])
            
            return JsonResponse({'success': True, 'channels': channels})
    
    return JsonResponse(result)


@login_required
@require_http_methods(["POST"])
def api_get_messages(request):
    """Get messages from a channel."""
    data = json.loads(request.body)
    channel_id = data.get('channel_id')
    
    if not channel_id:
        return JsonResponse({'success': False, 'error': 'Channel ID required'})
    
    result = _make_mm_request(f"/channels/{channel_id}/posts", method='GET', user=request.user)
    
    if result['success']:
        posts = result['data'].get('posts', [])
        # Convert to chronological order
        posts.sort(key=lambda x: x.get('create_at', 0))
        return JsonResponse({'success': True, 'messages': posts})
    
    return JsonResponse(result)


@login_required
@require_http_methods(["POST"])
def api_send_message(request):
    """Send message to Mattermost channel."""
    data = json.loads(request.body)
    channel_id = data.get('channel_id')
    message = data.get('message', '').strip()
    
    if not channel_id:
        return JsonResponse({'success': False, 'error': 'Channel ID required'})
    
    if not message:
        return JsonResponse({'success': False, 'error': 'Сообщение не может быть пустым'})
    
    post_data = {
        'channel_id': channel_id,
        'message': message
    }
    
    result = _make_mm_request('/posts', data=post_data, method='POST', user=request.user)
    
    if result['success']:
        # Log the message
        MattermostMessage.objects.create(
            message=message,
            channel=channel_id,
            sender=request.user,
            success=True
        )
    
    return JsonResponse(result)


@login_required
@require_http_methods(["POST"])
def test_connection(request):
    """Test Mattermost connection with user credentials."""
    mm_url = SystemSetting.get_mattermost_url()
    webhook_url = SystemSetting.get_mattermost_webhook_url()
    bot_token = SystemSetting.get_mattermost_bot_token()
    
    result = {
        'mm_url_configured': bool(mm_url),
        'webhook_configured': bool(webhook_url),
        'bot_token_configured': bool(bot_token),
        'ssl_verification': SystemSetting.is_ssl_verification_enabled(),
    }
    
    # Test user credentials
    creds = _get_user_mm_credentials(request.user)
    if creds:
        result['user_credentials'] = '✅ Настроены'
        test_result = _make_mm_request('/users/me', method='GET', user=request.user)
        result['user_connection'] = '✅ Успешно' if test_result['success'] else f"❌ {test_result.get('error', '')}"
    else:
        result['user_credentials'] = '❌ Не настроены'
        result['user_connection'] = '❌ Нет учетных данных'
    
    # Test system settings
    if mm_url:
        try:
            verify_ssl = SystemSetting.is_ssl_verification_enabled()
            response = requests.get(mm_url, verify=verify_ssl, timeout=5)
            result['server_reachable'] = f"✅ HTTP {response.status_code}"
        except Exception as e:
            result['server_reachable'] = f"❌ {str(e)}"
    else:
        result['server_reachable'] = '❌ URL не указан'
    
    return JsonResponse(result)
