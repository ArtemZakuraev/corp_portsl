"""Mattermost Integration app views - Modern, elegant interface."""
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.paginator import Paginator
from django.contrib import messages
import json
import logging

from .models import MattermostMessage, get_mattermost_client, MattermostConfig

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def dashboard(request):
    """
    Modern Mattermost integration dashboard with statistics and controls.
    Beautiful, fast, and user-friendly interface.
    """
    client = get_mattermost_client()
    
    # Get recent messages
    recent_messages = MattermostMessage.objects.select_related('sender').all()[:10]
    
    # Calculate statistics
    total_messages = MattermostMessage.objects.count()
    successful_messages = MattermostMessage.objects.filter(success=True).count()
    failed_messages = total_messages - successful_messages
    success_rate = (successful_messages / total_messages * 100) if total_messages > 0 else 0
    
    # Get messages by channel
    channel_stats = {}
    for msg in MattermostMessage.objects.values('channel').annotate(
        count=models.Count('id')
    )[:5]:
        channel_stats[msg['channel']] = msg['count']
    
    context = {
        'client': client,
        'recent_messages': recent_messages,
        'total_messages': total_messages,
        'successful_messages': successful_messages,
        'failed_messages': failed_messages,
        'success_rate': round(success_rate, 1),
        'channel_stats': channel_stats,
        'config': client.config,
    }
    
    return render(request, 'mattermost/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def send_message(request):
    """
    Elegant message sending interface with real-time feedback.
    """
    client = get_mattermost_client()
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            channel = data.get('channel', client.config.default_channel)
            message_text = data.get('message', '')
            username = data.get('username') or None
            
            if not message_text.strip():
                return JsonResponse({
                    'success': False,
                    'error': 'Сообщение не может быть пустым'
                }, status=400)
            
            success = client.send_message(
                message=message_text,
                channel=channel,
                username=username,
                use_cache=False  # Don't cache manual messages
            )
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Сообщение успешно отправлено!',
                    'timestamp': datetime.now().isoformat()
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Не удалось отправить сообщение. Проверьте логи.'
                }, status=500)
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    # GET request - show form
    context = {
        'default_channel': client.config.default_channel,
        'channels': [
            client.config.default_channel,
            client.config.news_channel,
            client.config.tasks_channel,
            client.config.meetings_channel,
        ]
    }
    
    return render(request, 'mattermost/send_message.html', context)


@login_required
@require_http_methods(["POST"])
def test_connection(request):
    """Test Mattermost connection with detailed results."""
    client = get_mattermost_client()
    result = client.test_connection()
    
    if result['success']:
        messages.success(request, f"Соединение успешно! Время ответа: {result['response_time_ms']:.2f} мс")
    else:
        messages.error(request, f"Ошибка соединения: {result.get('error', 'Неизвестная ошибка')}")
    
    return JsonResponse(result)


@login_required
@require_http_methods(["GET"])
def message_log(request):
    """
    Beautiful message log with filtering and pagination.
    """
    from django.db.models import Count
    
    # Get filters from request
    channel_filter = request.GET.get('channel', '')
    success_filter = request.GET.get('success', '')
    search_query = request.GET.get('search', '')
    
    # Build queryset
    queryset = MattermostMessage.objects.select_related('sender').all()
    
    if channel_filter:
        queryset = queryset.filter(channel=channel_filter)
    
    if success_filter in ['true', 'false']:
        queryset = queryset.filter(success=(success_filter == 'true'))
    
    if search_query:
        queryset = queryset.filter(
            models.Q(message__icontains=search_query) |
            models.Q(channel__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(queryset.order_by('-sent_at'), 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Get unique channels for filter dropdown
    channels = MattermostMessage.objects.values_list('channel', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'channels': channels,
        'current_channel': channel_filter,
        'current_success': success_filter,
        'search_query': search_query,
        'total_count': queryset.count(),
    }
    
    return render(request, 'mattermost/message_log.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def mattermost_webhook(request):
    """
    Handle incoming webhook from Mattermost.
    Enhanced with better error handling and response formatting.
    """
    try:
        data = json.loads(request.body)
        
        # Log the incoming webhook
        logger.info(f"Mattermost webhook received: {data}")
        
        # Extract useful information from the payload
        text = data.get('text', '')
        user_id = data.get('user_id', '')
        channel_id = data.get('channel_id', '')
        command = data.get('command', '')
        
        # Process the command (implement your logic here)
        response_data = {
            'text': f'Command received: {command}',
            'response_type': 'in_channel',
            'attachments': [{
                'color': '#4f46e5',
                'fields': [{
                    'title': 'Status',
                    'value': '✅ Success',
                    'short': True
                }]
            }]
        }
        
        return JsonResponse(response_data)
    
    except json.JSONDecodeError:
        logger.error("Invalid JSON in Mattermost webhook")
        return HttpResponseBadRequest("Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing Mattermost webhook: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# Import models for template access
from django.db import models
from datetime import datetime
