"""
Mattermost Integration App - Modern, Fast, and Beautiful Interface

This app provides seamless integration with Mattermost chat platform.

Features:
- High-performance client with connection pooling
- Caching to prevent duplicate messages
- Beautiful glassmorphism UI
- Real-time connection testing
- Message logging with filtering
- Statistics dashboard

Usage:
    from mattermost_integration import get_mattermost_client
    
    client = get_mattermost_client()
    client.send_message("Hello, World!", channel="town-square")
    
Or use the legacy functions for backward compatibility:
    from mattermost_integration.models import send_mattermost_message
    send_mattermost_message("town-square", "Hello!")
"""

__version__ = '2.0.0'
__author__ = 'Corporate Portal Team'

# Lazy imports to avoid AppRegistryNotReady error during Django startup
def __getattr__(name):
    if name in __all__:
        from .models import (
            MattermostClient,
            MattermostConfig,
            get_mattermost_client,
            send_mattermost_message,
            send_notification_to_user,
            send_news_notification,
            send_task_notification,
            send_meeting_reminder,
        )
        return {
            'MattermostClient': MattermostClient,
            'MattermostConfig': MattermostConfig,
            'get_mattermost_client': get_mattermost_client,
            'send_mattermost_message': send_mattermost_message,
            'send_notification_to_user': send_notification_to_user,
            'send_news_notification': send_news_notification,
            'send_task_notification': send_task_notification,
            'send_meeting_reminder': send_meeting_reminder,
        }[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'MattermostClient',
    'MattermostConfig',
    'get_mattermost_client',
    'send_mattermost_message',
    'send_notification_to_user',
    'send_news_notification',
    'send_task_notification',
    'send_meeting_reminder',
]