from __future__ import annotations

from typing import Dict, Any

from .models import UserProfile


def user_theme(request) -> Dict[str, Any]:
    """
    Добавляет в контекст настройки темы текущего пользователя.
    Используется для переопределения цветов портала.
    """
    theme = {
        "mode": "default",
        "primary_color": "",
        "sidebar_bg_color": "",
        "header_bg_color": "",
    }

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            profile: UserProfile = user.profile  # type: ignore[assignment]
        except UserProfile.DoesNotExist:
            profile = None

        if profile:
            theme["mode"] = profile.theme_mode
            theme["primary_color"] = profile.theme_primary_color or ""
            theme["sidebar_bg_color"] = profile.theme_sidebar_bg_color or ""
            theme["header_bg_color"] = profile.theme_header_bg_color or ""

    return {"user_theme": theme}


def user_sidebar_settings(request) -> Dict[str, Any]:
    """
    Добавляет в контекст настройки сайдбара текущего пользователя.
    """
    sidebar_settings = {
        "custom_enabled": False,
        "width": 280,
        "height": "calc(100vh - 64px)",
    }

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            profile: UserProfile = user.profile  # type: ignore[assignment]
        except UserProfile.DoesNotExist:
            profile = None

        if profile and profile.sidebar_custom_enabled:
            sidebar_settings["custom_enabled"] = True
            sidebar_settings["width"] = profile.sidebar_width or 280
            sidebar_settings["height"] = profile.sidebar_height or "calc(100vh - 64px)"

    return {"user_sidebar_settings": sidebar_settings}


def user_menu_settings(request) -> Dict[str, Any]:
    """
    Добавляет в контекст настройки меню текущего пользователя.
    """
    menu_settings = {
        "items_settings": {},
        "show_favorites_only": False,
    }

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            profile: UserProfile = user.profile  # type: ignore[assignment]
        except UserProfile.DoesNotExist:
            profile = None

        if profile:
            import json
            items_settings = profile.menu_items_settings or {}
            # Убеждаемся, что это словарь
            if isinstance(items_settings, str):
                try:
                    items_settings = json.loads(items_settings)
                except:
                    items_settings = {}
            # Преобразуем в JSON строку для безопасной передачи в шаблон
            menu_settings["items_settings"] = json.dumps(items_settings) if items_settings else "{}"
            menu_settings["show_favorites_only"] = profile.menu_show_favorites_only or False

    return {"user_menu_settings": menu_settings}


def user_tasks_count(request) -> Dict[str, Any]:
    """
    Добавляет в контекст количество невыполненных задач пользователя.
    Учитываются задачи, которые пользователь создал сам себе, и задачи, назначенные ему руководителями.
    """
    task_count = 0
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            # Подсчитываем все задачи, кроме выполненных (new и in_progress)
            from tasks.models import Task
            from django.db import models
            task_count = Task.objects.filter(
                models.Q(created_by=user) | models.Q(assignee=user)
            ).exclude(status="done").count()
        except Exception:
            task_count = 0
    
    return {"user_tasks_count": task_count}


def user_meetings_today_count(request) -> Dict[str, Any]:
    """
    Добавляет в контекст количество встреч пользователя на сегодня.
    """
    meetings_count = 0
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            from datetime import datetime, date
            from organization.caldav_utils import get_user_meetings
            from organization.models import CaldavSettings
            
            caldav_settings = CaldavSettings.get_solo()
            # Проверяем, настроен ли CalDAV сервер и настройки пользователя
            if caldav_settings.server_url:
                try:
                    profile = user.profile
                    if profile.caldav_email and profile.caldav_password:
                        today = date.today()
                        start_datetime = datetime.combine(today, datetime.min.time())
                        end_datetime = datetime.combine(today, datetime.max.time())
                        meetings_today = get_user_meetings(user, start_datetime, end_datetime)
                        if meetings_today:
                            # Фильтруем встречи, которые действительно на сегодня
                            today_meetings = []
                            for meeting in meetings_today:
                                meeting_start = meeting.get("start")
                                if meeting_start:
                                    if isinstance(meeting_start, datetime):
                                        meeting_date = meeting_start.date()
                                    elif isinstance(meeting_start, date):
                                        meeting_date = meeting_start
                                    else:
                                        continue
                                    if meeting_date == today:
                                        today_meetings.append(meeting)
                            meetings_count = len(today_meetings)
                except (AttributeError, Exception):
                    meetings_count = 0
        except Exception:
            meetings_count = 0
    
    return {"user_meetings_today_count": meetings_count}


def user_chat_notifications_count(request) -> Dict[str, Any]:
    """
    Добавляет в контекст количество непрочитанных сообщений из чата Mattermost.
    """
    notifications_count = 0
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        try:
            from organization.mattermost_client import MattermostClient
            from organization.models import MattermostSettings
            from accounts.models import UserProfile
            
            profile = user.profile
            mm_settings = MattermostSettings.get_solo()
            
            if mm_settings.server_url and profile.mattermost_username and profile.mattermost_password:
                # Создаем клиент с профилем пользователя
                client = MattermostClient(profile)
                if client.login():
                    # Получаем все каналы
                    channels = client.get_channels()
                    # Подсчитываем непрочитанные сообщения
                    for channel in channels:
                        channel_id = channel.get("id", "")
                        if channel_id:
                            unread_count = client.get_channel_unread_count(channel_id)
                            notifications_count += unread_count
        except Exception:
            notifications_count = 0
    
    return {"user_chat_notifications_count": notifications_count}




