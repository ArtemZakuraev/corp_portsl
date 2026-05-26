"""
Mattermost Integration app - Chat and notifications integration.
Provides seamless integration with Mattermost chat platform.
Modern, fast, and elegant implementation with connection pooling and async support.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.cache import cache
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Import requests lazily to avoid blocking
try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    
    # Create a session with connection pooling and retry logic
    _session = None
    
    def get_mattermost_session():
        """Get or create a reusable session with connection pooling."""
        global _session
        if _session is None:
            _session = requests.Session()
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["POST", "GET"]
            )
            adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
            _session.mount("http://", adapter)
            _session.mount("https://", adapter)
        return _session
        
except ImportError:
    logger.warning("requests library not installed. Mattermost integration disabled.")
    get_mattermost_session = None


@dataclass
class MattermostConfig:
    """Configuration container for Mattermost integration."""
    webhook_url: Optional[str] = None
    api_url: Optional[str] = None
    token: Optional[str] = None
    default_channel: str = 'town-square'
    news_channel: str = 'news'
    tasks_channel: str = 'tasks'
    meetings_channel: str = 'meetings'
    timeout: int = 10
    username: str = 'Corporate Portal'
    icon_url: Optional[str] = None
    
    @classmethod
    def from_settings(cls) -> 'MattermostConfig':
        """Create config from Django settings."""
        return cls(
            webhook_url=getattr(settings, 'MATTERMOST_WEBHOOK_URL', None) or getattr(settings, 'MATTERMOST_URL', ''),
            api_url=getattr(settings, 'MATTERMOST_API_URL', None),
            token=getattr(settings, 'MATTERMOST_TOKEN', ''),
            default_channel=getattr(settings, 'MATTERMOST_DEFAULT_CHANNEL', 'town-square'),
            news_channel=getattr(settings, 'MATTERMOST_NEWS_CHANNEL', 'news'),
            tasks_channel=getattr(settings, 'MATTERMOST_TASKS_CHANNEL', 'tasks'),
            meetings_channel=getattr(settings, 'MATTERMOST_MEETINGS_CHANNEL', 'meetings'),
            timeout=getattr(settings, 'MATTERMOST_TIMEOUT', 10),
            username=getattr(settings, 'MATTERMOST_BOT_USERNAME', 'Corporate Portal'),
            icon_url=getattr(settings, 'MATTERMOST_ICON_URL', None),
        )


class MattermostClient:
    """
    Modern, high-performance Mattermost client with connection pooling,
    caching, and elegant API.
    """
    
    def __init__(self, config: Optional[MattermostConfig] = None):
        self.config = config or MattermostConfig.from_settings()
        self._cache_prefix = 'mattermost_'
    
    def _get_cache_key(self, key: str) -> str:
        return f"{self._cache_prefix}{key}"
    
    def _set_cache(self, key: str, value: Any, timeout: int = 300) -> None:
        cache.set(self._get_cache_key(key), value, timeout)
    
    def _get_cache(self, key: str, default: Any = None) -> Any:
        return cache.get(self._get_cache_key(key), default)
    
    def send_message(
        self,
        message: str,
        channel: Optional[str] = None,
        username: Optional[str] = None,
        icon_url: Optional[str] = None,
        use_cache: bool = True,
        cache_timeout: int = 60
    ) -> bool:
        """
        Send message to Mattermost channel via webhook.
        
        Args:
            message: Message text (supports Markdown)
            channel: Channel name (defaults to config.default_channel)
            username: Optional username override
            icon_url: Optional icon URL override
            use_cache: Whether to cache identical messages briefly to prevent spam
            cache_timeout: Cache timeout in seconds
            
        Returns:
            bool: True if message was sent successfully
        """
        if not self.config.webhook_url:
            logger.warning("Mattermost webhook URL not configured")
            return False
        
        # Anti-spam cache
        if use_cache:
            cache_key = f"msg_{hash(message + channel)}"
            if self._get_cache(cache_key):
                logger.info(f"Duplicate message cached, skipping: {message[:50]}...")
                return True
        
        channel = channel or self.config.default_channel
        payload = {
            'channel': channel,
            'text': message,
            'username': username or self.config.username,
        }
        
        if icon_url or self.config.icon_url:
            payload['icon_url'] = icon_url or self.config.icon_url
        
        try:
            session = get_mattermost_session()
            response = session.post(
                self.config.webhook_url,
                json=payload,
                timeout=self.config.timeout,
                headers={'Content-Type': 'application/json'}
            )
            success = response.status_code == 200
            
            # Log the message
            MattermostMessage.objects.create(
                channel=channel,
                message=message,
                success=success,
                response_data=response.text[:1000] if response.text else ''
            )
            
            if success and use_cache:
                self._set_cache(cache_key, True, cache_timeout)
            
            if not success:
                logger.error(f"Mattermost API error: {response.status_code} - {response.text}")
            
            return success
        
        except requests.RequestException as e:
            logger.error(f"Failed to send Mattermost message: {e}")
            MattermostMessage.objects.create(
                channel=channel,
                message=message,
                success=False,
                response_data=str(e)
            )
            return False
    
    def send_to_user(self, user: User, message: str, channel: Optional[str] = None) -> bool:
        """Send direct message to specific user via Mattermost."""
        target_channel = channel or f"@{user.username}"
        formatted_message = f"**Уведомление для {user.get_full_name()}**\n\n{message}"
        return self.send_message(formatted_message, channel=target_channel)
    
    def send_news_notification(self, news_item) -> bool:
        """Send notification about new news article."""
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        message = (
            f"📰 **Новая новость: {news_item.title}**\n\n"
            f"{news_item.excerpt or news_item.content[:200]}...\n\n"
            f"[Читать далее]({site_url}/news/{news_item.pk}/)"
        )
        return self.send_message(message, channel=self.config.news_channel)
    
    def send_task_notification(self, task, notify_users: Optional[List[User]] = None) -> bool:
        """Send notification about task assignment or update."""
        if notify_users is None and hasattr(task, 'assignee') and task.assignee:
            notify_users = [task.assignee]
        
        if not notify_users:
            return False
        
        status_emoji = {
            'new': '🆕',
            'in_progress': '⏳',
            'review': '👀',
            'done': '✅',
            'cancelled': '❌',
        }
        
        emoji = status_emoji.get(task.status, '📋')
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        message = (
            f"{emoji} **Задача: {task.title}**\n\n"
            f"*Статус:* {task.get_status_display()}\n"
            f"*Приоритет:* {task.get_priority_display()}\n"
        )
        
        if hasattr(task, 'assignee') and task.assignee:
            message += f"*Исполнитель:* @{task.assignee.username}\n"
        
        if hasattr(task, 'due_date') and task.due_date:
            message += f"*Срок:* {task.due_date.strftime('%d.%m.%Y %H:%M')}\n"
        
        message += f"\n[Открыть задачу]({site_url}/tasks/{task.pk}/)"
        
        return self.send_message(message, channel=self.config.tasks_channel)
    
    def send_meeting_reminder(self, meeting) -> bool:
        """Send meeting reminder to participants."""
        participants = meeting.participants.filter(response='accepted')
        participant_mentions = ' '.join([f"@{p.user.username}" for p in participants if p.user])
        
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        message = (
            f"📅 **Напоминание о встрече: {meeting.title}**\n\n"
            f"*Начало:* {meeting.start_time.strftime('%d.%m.%Y %H:%M')}\n"
            f"*Окончание:* {meeting.end_time.strftime('%H:%M')}\n"
        )
        
        if hasattr(meeting, 'room') and meeting.room:
            message += f"*Место:* {meeting.room.name}\n"
        
        if hasattr(meeting, 'meeting_link') and meeting.meeting_link:
            message += f"*Ссылка:* {meeting.meeting_link}\n"
        
        if participant_mentions:
            message += f"\n{participant_mentions}"
        
        return self.send_message(message, channel=self.config.meetings_channel)
    
    def test_connection(self) -> Dict[str, Any]:
        """Test Mattermost connection and return status."""
        result = {
            'success': False,
            'error': None,
            'response_time_ms': None,
            'webhook_configured': bool(self.config.webhook_url),
        }
        
        if not self.config.webhook_url:
            result['error'] = "Webhook URL not configured"
            return result
        
        start_time = datetime.now()
        
        try:
            session = get_mattermost_session()
            response = session.post(
                self.config.webhook_url,
                json={
                    'channel': self.config.default_channel,
                    'text': '🔌 **Тест соединения**\n\nСоединение с Mattermost успешно установлено!',
                },
                timeout=self.config.timeout,
            )
            
            end_time = datetime.now()
            result['response_time_ms'] = (end_time - start_time).total_seconds() * 1000
            result['success'] = response.status_code == 200
            result['status_code'] = response.status_code
            
            if not result['success']:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
            
        except requests.RequestException as e:
            result['error'] = str(e)
        
        return result


# Singleton instance for reuse
_mattermost_client_instance = None

def get_mattermost_client() -> MattermostClient:
    """Get or create singleton Mattermost client instance."""
    global _mattermost_client_instance
    if _mattermost_client_instance is None:
        _mattermost_client_instance = MattermostClient()
    return _mattermost_client_instance


# Legacy function wrappers for backward compatibility
def send_mattermost_message(channel, message, username=None, icon_url=None):
    """Legacy wrapper for backward compatibility."""
    client = get_mattermost_client()
    return client.send_message(message, channel=channel, username=username, icon_url=icon_url)

def send_notification_to_user(user, message, channel=None):
    """Legacy wrapper for backward compatibility."""
    client = get_mattermost_client()
    return client.send_to_user(user, message, channel=channel)

def send_news_notification(news_item):
    """Legacy wrapper for backward compatibility."""
    client = get_mattermost_client()
    return client.send_news_notification(news_item)

def send_task_notification(task, notify_users=None):
    """Legacy wrapper for backward compatibility."""
    client = get_mattermost_client()
    return client.send_task_notification(task, notify_users=notify_users)

def send_meeting_reminder(meeting):
    """Legacy wrapper for backward compatibility."""
    client = get_mattermost_client()
    return client.send_meeting_reminder(meeting)


class MattermostMessage(models.Model):
    """Log of messages sent to Mattermost."""
    
    channel = models.CharField(
        max_length=200,
        verbose_name=_('Канал'),
        db_index=True
    )
    message = models.TextField(verbose_name=_('Сообщение'))
    sender = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mattermost_messages',
        verbose_name=_('Отправитель')
    )
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Отправлено'), db_index=True)
    success = models.BooleanField(default=False, verbose_name=_('Успешно'), db_index=True)
    response_data = models.TextField(
        blank=True,
        verbose_name=_('Ответ сервера')
    )
    response_time_ms = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Время ответа (мс)')
    )
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = _('Mattermost сообщение')
        verbose_name_plural = _('Mattermost сообщения')
        indexes = [
            models.Index(fields=['channel', '-sent_at']),
            models.Index(fields=['success', '-sent_at']),
            models.Index(fields=['-sent_at']),
        ]
    
    def __str__(self):
        status_icon = "✅" if self.success else "❌"
        return f"{status_icon} {self.channel}: {self.message[:50]}"
    
    def get_truncated_message(self):
        """Get truncated message for display."""
        if len(self.message) > 100:
            return self.message[:100] + "..."
        return self.message
    
    def get_response_time_display(self):
        """Get formatted response time."""
        if self.response_time_ms:
            return f"{self.response_time_ms:.2f} мс"
        return "—"
