"""
Утилиты для работы с CalDAV сервером.
Получение календарей и событий через прямую ссылку на календарь пользователя.
URL календаря формируется по шаблону: $server/SOGo/dav/$user_email/Calendar/personal/
"""
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from django.contrib.auth.models import User
from .models import CaldavSettings

logger = logging.getLogger(__name__)

try:
    import caldav
    CALDAV_AVAILABLE = True
except ImportError:
    CALDAV_AVAILABLE = False
    logger.warning("Библиотека caldav не установлена. Установите её: pip install caldav")


def get_caldav_client(server_url: str, user_email: str, user_password: str):
    """
    Создаёт клиент CalDAV для подключения к серверу.
    
    Args:
        server_url: Базовый URL CalDAV сервера
        user_email: Email пользователя для авторизации
        user_password: Пароль пользователя для авторизации
    
    Returns:
        caldav.DAVClient или None в случае ошибки
    """
    if not CALDAV_AVAILABLE:
        logger.error("Библиотека caldav не установлена")
        return None
    
    if not server_url:
        logger.error("URL CalDAV сервера не настроен")
        return None
    
    if not user_email or not user_password:
        logger.error("Не указаны учетные данные пользователя для подключения к CalDAV")
        return None
    
    try:
        client = caldav.DAVClient(
            url=server_url,
            username=user_email,
            password=user_password,
        )
        return client
    except Exception as e:
        logger.error(f"Ошибка при создании CalDAV клиента: {e}")
        return None


def get_calendar_by_url(client, calendar_url: str):
    """
    Получает календарь пользователя по прямому URL.
    
    Args:
        client: CalDAV клиент
        calendar_url: Прямой URL календаря (например: https://server/SOGo/dav/user@example.com/Calendar/personal/)
    
    Returns:
        Calendar или None, если календарь не найден
    """
    if not client:
        return None
    
    try:
        # Используем прямую ссылку на календарь
        calendar = client.calendar(url=calendar_url)
        return calendar
    except Exception as e:
        logger.error(f"Ошибка при получении календаря по URL {calendar_url}: {e}")
        return None


def get_events_from_calendar(calendar, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Получает события из календаря CalDAV.
    
    Args:
        calendar: Календарь CalDAV
        start_date: Начальная дата для фильтрации (по умолчанию - сегодня)
        end_date: Конечная дата для фильтрации (по умолчанию - через месяц)
    
    Returns:
        Список словарей с информацией о событиях
    """
    if not calendar:
        return []
    
    if start_date is None:
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if end_date is None:
        end_date = start_date + timedelta(days=30)
    
    events_list = []
    
    try:
        # Получаем события из календаря
        events = calendar.search(
            start=start_date,
            end=end_date,
            event=True,
        )
        
        for event in events:
            try:
                vevent = event.icalendar_component
                
                # Извлекаем информацию о событии
                event_data = {
                    "summary": str(vevent.get("summary", "")) if vevent.get("summary") else "Без названия",
                    "description": str(vevent.get("description", "")) if vevent.get("description") else "",
                    "location": str(vevent.get("location", "")) if vevent.get("location") else "",
                    "start": None,
                    "end": None,
                    "url": str(event.url) if hasattr(event, "url") else "",
                }
                
                # Обрабатываем дату начала
                dtstart = vevent.get("dtstart")
                if dtstart:
                    if hasattr(dtstart.dt, "date"):
                        event_data["start"] = dtstart.dt.date()
                    else:
                        event_data["start"] = dtstart.dt
                
                # Обрабатываем дату окончания
                dtend = vevent.get("dtend")
                if dtend:
                    if hasattr(dtend.dt, "date"):
                        event_data["end"] = dtend.dt.date()
                    else:
                        event_data["end"] = dtend.dt
                
                # Если нет даты окончания, используем дату начала
                if not event_data["end"] and event_data["start"]:
                    if isinstance(event_data["start"], datetime):
                        event_data["end"] = event_data["start"] + timedelta(hours=1)
                    else:
                        event_data["end"] = event_data["start"]
                
                events_list.append(event_data)
            except Exception as e:
                logger.warning(f"Ошибка при обработке события: {e}")
                continue
        
        # Сортируем события по дате начала
        events_list.sort(key=lambda x: x["start"] if x["start"] else datetime.min)
        
    except Exception as e:
        logger.error(f"Ошибка при получении событий из календаря: {e}")
    
    return events_list


def get_user_meetings(user: User, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
    """
    Получает встречи пользователя из CalDAV календаря.
    Использует настройки пользователя (caldav_email и caldav_password) из профиля.
    URL календаря формируется по шаблону: $server/SOGo/dav/$user_email/Calendar/personal/
    
    Args:
        user: Пользователь Django
        start_date: Начальная дата для фильтрации
        end_date: Конечная дата для фильтрации
    
    Returns:
        Список словарей с информацией о встречах
    """
    # Получаем настройки CalDAV сервера из системных настроек
    caldav_settings = CaldavSettings.get_solo()
    
    if not caldav_settings.server_url:
        logger.warning("CalDAV сервер не настроен в системных настройках")
        return []
    
    # Получаем настройки пользователя из профиля
    try:
        profile = user.profile
    except AttributeError:
        logger.warning(f"У пользователя {user.username} нет профиля")
        return []
    
    user_caldav_email = profile.caldav_email
    user_caldav_password = profile.caldav_password
    
    if not user_caldav_email or not user_caldav_password:
        logger.warning(f"У пользователя {user.username} не настроены email или пароль для CalDAV в профиле")
        return []
    
    # Формируем URL календаря по шаблону: $server/SOGo/dav/$user_email/Calendar/personal/
    server_url = caldav_settings.server_url.rstrip('/')
    calendar_url = f"{server_url}/SOGo/dav/{user_caldav_email}/Calendar/personal/"
    
    # Создаём клиент CalDAV, используя настройки пользователя
    client = get_caldav_client(server_url, user_caldav_email, user_caldav_password)
    
    if not client:
        return []
    
    # Получаем календарь по прямому URL
    calendar = get_calendar_by_url(client, calendar_url)
    
    if not calendar:
        logger.warning(f"Календарь для пользователя {user_caldav_email} не найден по URL: {calendar_url}")
        return []
    
    # Получаем события из календаря
    events = get_events_from_calendar(calendar, start_date, end_date)
    
    return events

