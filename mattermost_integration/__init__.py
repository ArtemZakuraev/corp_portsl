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