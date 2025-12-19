"""
Утилиты для работы с Mattermost API.
"""
import requests
from typing import Dict, List, Optional, Any
from django.conf import settings
from .models import MattermostSettings
from accounts.models import UserProfile


class MattermostClient:
    """
    Клиент для работы с Mattermost API.
    """

    def __init__(self, user_profile: UserProfile):
        """
        Инициализация клиента с учетными данными пользователя.
        
        Args:
            user_profile: Профиль пользователя с настройками Mattermost
        """
        self.user_profile = user_profile
        self.settings = MattermostSettings.get_solo()
        self.base_url = self.settings.server_url.rstrip('/')
        self.api_version = self.settings.api_version
        self.token: Optional[str] = None
        self.user_id: Optional[str] = None
        # Используем сессию для сохранения cookies
        self.session = requests.Session()
        # Настраиваем проверку SSL сертификата
        self.session.verify = self.settings.verify_ssl
        
        # Отключаем предупреждения urllib3, если проверка SSL отключена
        if not self.settings.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Mattermost SSL verification is disabled for {self.base_url}. This is not recommended for production.")

    def _get_api_url(self, endpoint: str) -> str:
        """Формирует полный URL для API запроса."""
        return f"{self.base_url}/api/{self.api_version}/{endpoint.lstrip('/')}"

    def login(self) -> bool:
        """
        Авторизация на сервере Mattermost.
        
        Returns:
            True если авторизация успешна, False в противном случае
        """
        if not self.user_profile.mattermost_username or not self.user_profile.mattermost_password:
            return False

        url = self._get_api_url("/users/login")
        data = {
            "login_id": self.user_profile.mattermost_username.strip(),
            "password": self.user_profile.mattermost_password.strip(),
        }

        try:
            # Используем сессию для сохранения cookies
            response = self.session.post(url, json=data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                # Mattermost возвращает токен в заголовке Token (с заглавной буквы)
                self.token = response.headers.get("Token", "") or response.headers.get("token", "")
                
                # Если токен не в заголовке, проверяем cookies
                # Mattermost может использовать cookies для авторизации
                cookies = response.cookies
                if 'MMAUTHTOKEN' in cookies:
                    # Если токен в cookies, используем его
                    if not self.token:
                        self.token = cookies['MMAUTHTOKEN'].value
                elif 'MMCSRF' in cookies:
                    if not self.token:
                        self.token = cookies['MMCSRF'].value
                
                self.user_id = result.get("id", "")
                
                # Проверяем, что получили и токен, и user_id
                # Если токен не найден, но есть cookies, считаем авторизацию успешной
                # (сессия будет использовать cookies автоматически)
                if not self.token:
                    # Проверяем, есть ли хотя бы cookies для авторизации
                    has_auth_cookies = 'MMAUTHTOKEN' in cookies or 'MMCSRF' in cookies
                    if has_auth_cookies and self.user_id:
                        # Если есть cookies и user_id, авторизация успешна
                        # Токен не обязателен, если используются cookies
                        return True
                    else:
                        import logging
                        logger = logging.getLogger(__name__)
                        logger.warning(f"Mattermost login: token not found in headers or cookies. Headers: {dict(response.headers)}, Cookies: {list(cookies.keys())}")
                        return False
                
                return bool(self.token and self.user_id)
            else:
                # Логируем ошибку для отладки
                import logging
                logger = logging.getLogger(__name__)
                try:
                    error_text = response.text
                except:
                    error_text = "No response text"
                logger.error(f"Mattermost login failed: {response.status_code} - {error_text}")
        except Exception as e:
            # Логируем исключение для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Mattermost login exception: {str(e)}", exc_info=True)

        return False

    def _get_headers(self) -> Dict[str, str]:
        """Возвращает заголовки для API запросов."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.token:
            # Mattermost может использовать разные форматы авторизации
            # Пробуем оба варианта для совместимости
            headers["Authorization"] = f"Bearer {self.token}"
            # Также добавляем токен в заголовок Token (некоторые версии Mattermost требуют это)
            headers["Token"] = self.token
        # Если токена нет, но есть cookies в сессии, они будут использованы автоматически
        return headers

    def get_channels(self) -> List[Dict[str, Any]]:
        """
        Получает список всех каналов пользователя (включая прямые).
        
        Returns:
            Список каналов
        """
        if not self.token:
            if not self.login():
                return []

        # Получаем каналы пользователя
        url = self._get_api_url(f"/users/{self.user_id}/channels")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                channels = response.json()
                # Сортируем каналы: сначала обычные, потом прямые
                regular = [ch for ch in channels if ch.get("type") != "D"]
                direct = [ch for ch in channels if ch.get("type") == "D"]
                return regular + direct
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting channels: {str(e)}")

        return []

    def get_teams(self) -> List[Dict[str, Any]]:
        """
        Получает список команд пользователя.
        
        Returns:
            Список команд
        """
        if not self.token:
            if not self.login():
                return []

        url = self._get_api_url(f"/users/{self.user_id}/teams")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        return []

    def get_channel_posts(self, channel_id: str, limit: int = 60) -> List[Dict[str, Any]]:
        """
        Получает сообщения из канала.
        
        Args:
            channel_id: ID канала
            limit: Количество сообщений (по умолчанию 60)
            
        Returns:
            Список сообщений с обработанными датами
        """
        if not self.token:
            if not self.login():
                return []

        url = self._get_api_url(f"/channels/{channel_id}/posts")
        params = {
            "page": 0,
            "per_page": limit,
        }
        try:
            response = self.session.get(url, headers=self._get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                result = response.json()
                posts = result.get("posts", {})
                # Получаем информацию о пользователях для отображения имен
                user_ids = set()
                for post in posts.values():
                    user_ids.add(post.get("user_id", ""))
                
                users_map = {}
                for user_id in user_ids:
                    user_info = self.get_user(user_id)
                    if user_info:
                        users_map[user_id] = user_info.get("username", user_id)
                
                # Преобразуем словарь постов в список
                posts_list = []
                order = result.get("order", [])
                for post_id in order:
                    if post_id in posts:
                        post = posts[post_id]
                        # Преобразуем timestamp в миллисекундах в datetime
                        create_at = post.get("create_at", 0)
                        if create_at:
                            from datetime import datetime
                            try:
                                # Mattermost использует миллисекунды
                                dt = datetime.fromtimestamp(create_at / 1000)
                                post["create_at"] = dt
                            except (ValueError, OSError):
                                pass
                        # Заменяем user_id на username если доступен
                        user_id = post.get("user_id", "")
                        if user_id in users_map:
                            post["username"] = users_map[user_id]
                        
                        # Получаем информацию о файлах, если они есть
                        file_ids = post.get("file_ids", [])
                        if file_ids:
                            post["files"] = []
                            for file_id in file_ids:
                                file_info = self.get_file_info(file_id)
                                if file_info:
                                    post["files"].append(file_info)
                        
                        posts_list.append(post)
                return posts_list
        except Exception:
            pass

        return []

    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о пользователе.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Информация о пользователе или None
        """
        if not self.token:
            if not self.login():
                return None

        url = self._get_api_url(f"/users/{user_id}")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        return None

    def get_all_users(self, page: int = 0, per_page: int = 100) -> List[Dict[str, Any]]:
        """
        Получает список всех пользователей Mattermost.
        
        Args:
            page: Номер страницы (начинается с 0)
            per_page: Количество пользователей на странице
            
        Returns:
            Список пользователей
        """
        if not self.token:
            if not self.login():
                return []
        
        url = self._get_api_url("/users")
        params = {
            "page": page,
            "per_page": per_page,
            "sort": "username",
        }
        try:
            response = self.session.get(url, headers=self._get_headers(), params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting users: {str(e)}")
        return []

    def create_direct_channel(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Создает прямой канал (DM) с указанным пользователем.
        
        Args:
            user_id: ID пользователя, с которым создается канал
            
        Returns:
            Созданный канал или None
        """
        if not self.token:
            if not self.login():
                return None
        
        # Mattermost API для создания прямого канала
        url = self._get_api_url("/channels/direct")
        data = [self.user_id, user_id]
        try:
            response = self.session.post(url, headers=self._get_headers(), json=data, timeout=10)
            if response.status_code == 201:
                return response.json()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating direct channel: {str(e)}")
        return None

    def get_channel_members(self, channel_id: str) -> List[Dict[str, Any]]:
        """
        Получает список участников канала.
        
        Args:
            channel_id: ID канала
            
        Returns:
            Список участников
        """
        if not self.token:
            if not self.login():
                return []

        url = self._get_api_url(f"/channels/{channel_id}/members")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass

        return []

    def get_channel_unread_count(self, channel_id: str) -> int:
        """
        Получает количество непрочитанных сообщений в канале.
        
        Args:
            channel_id: ID канала
            
        Returns:
            Количество непрочитанных сообщений
        """
        if not self.token:
            if not self.login():
                return 0

        # Получаем информацию о канале и непрочитанных сообщениях
        url = self._get_api_url(f"/users/{self.user_id}/channels/{channel_id}/unread")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Mattermost возвращает количество непрочитанных сообщений
                return data.get("msg_count", 0)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting unread count for channel {channel_id}: {str(e)}")
        
        # Альтернативный способ: получаем информацию о канале
        try:
            url = self._get_api_url(f"/channels/{channel_id}")
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                channel_data = response.json()
                # Получаем информацию о членстве в канале
                member_url = self._get_api_url(f"/users/{self.user_id}/channels/{channel_id}/members/me")
                member_response = self.session.get(member_url, headers=self._get_headers(), timeout=10)
                if member_response.status_code == 200:
                    member_data = member_response.json()
                    # Вычисляем непрочитанные сообщения
                    total_msg_count = channel_data.get("total_msg_count", 0)
                    msg_count = member_data.get("msg_count", 0)
                    if total_msg_count > msg_count:
                        return total_msg_count - msg_count
        except Exception:
            pass

        return 0

    def get_file_info(self, file_id: str) -> Optional[Dict[str, Any]]:
        """
        Получает информацию о файле из Mattermost.
        
        Args:
            file_id: ID файла
            
        Returns:
            Информация о файле или None
        """
        if not self.token:
            if not self.login():
                return None
        
        url = self._get_api_url(f"/files/{file_id}/info")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=10)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting file info for {file_id}: {str(e)}")
        
        return None

    def download_file(self, file_id: str, save_path: str) -> bool:
        """
        Скачивает файл из Mattermost и сохраняет его локально.
        
        Args:
            file_id: ID файла
            save_path: Путь для сохранения файла
            
        Returns:
            True если файл успешно скачан, False в противном случае
        """
        if not self.token:
            if not self.login():
                return False
        
        url = self._get_api_url(f"/files/{file_id}")
        try:
            response = self.session.get(url, headers=self._get_headers(), timeout=30, stream=True)
            if response.status_code == 200:
                import os
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error downloading file {file_id}: {str(e)}")
        
        return False

    def send_message(self, channel_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Отправляет сообщение в канал.
        
        Args:
            channel_id: ID канала
            message: Текст сообщения
            
        Returns:
            Созданное сообщение или None
        """
        if not self.token:
            if not self.login():
                return None

        url = self._get_api_url("/posts")
        data = {
            "channel_id": channel_id,
            "message": message,
        }
        try:
            response = self.session.post(url, headers=self._get_headers(), json=data, timeout=10)
            if response.status_code == 201:
                return response.json()
        except Exception:
            pass

        return None

    def get_direct_channels(self, only_with_messages: bool = True) -> List[Dict[str, Any]]:
        """
        Получает список прямых каналов (DM) пользователя с информацией об участниках.
        
        Args:
            only_with_messages: Если True, возвращает только каналы с сообщениями
        
        Returns:
            Список прямых каналов с именами участников
        """
        if not self.token:
            if not self.login():
                return []

        # Получаем все каналы и фильтруем прямые
        all_channels = self.get_channels()
        direct_channels = [ch for ch in all_channels if ch.get("type") == "D"]
        
        # Для каждого прямого канала получаем информацию об участниках
        result_channels = []
        for channel in direct_channels:
            # В Mattermost имя прямого канала имеет формат: user1__user2 (сортированные ID)
            # Нужно найти другого участника
            channel_name = channel.get("name", "")
            
            # Получаем участников канала
            members = self.get_channel_members(channel.get("id", ""))
            # Находим второго участника (не текущего пользователя)
            other_user_id = None
            for member in members:
                member_user_id = member.get("user_id")
                if member_user_id and member_user_id != self.user_id:
                    other_user_id = member_user_id
                    break
            
            # Если не нашли через members, пытаемся извлечь из имени канала
            if not other_user_id and channel_name:
                # Формат имени: user1__user2 или user1_user2
                user_ids = channel_name.replace("__", "_").split("_")
                for uid in user_ids:
                    if uid and uid != self.user_id:
                        other_user_id = uid
                        break
            
            # Получаем информацию о другом пользователе
            if other_user_id:
                user_info = self.get_user(other_user_id)
                if user_info:
                    # Устанавливаем отображаемое имя
                    channel["other_user"] = user_info
                    # Формируем имя: сначала полное имя, потом username
                    full_name = ""
                    if user_info.get("first_name") or user_info.get("last_name"):
                        full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip()
                    channel["display_name"] = full_name or user_info.get("username", other_user_id)
                else:
                    channel["display_name"] = channel.get("name", "Unknown User")
            else:
                channel["display_name"] = channel.get("name", "Direct Message")
            
            # Получаем последнее сообщение для отображения превью
            posts = self.get_channel_posts(channel.get("id", ""), limit=1)
            if posts and len(posts) > 0:
                # Сохраняем последнее сообщение
                last_post = posts[0]
                channel["last_post"] = last_post
                # Сохраняем время последнего сообщения для сортировки
                # get_channel_posts уже преобразует create_at в datetime, но для сортировки нужен timestamp
                create_at = last_post.get("create_at")
                if hasattr(create_at, "timestamp"):
                    # Если это datetime объект, преобразуем в timestamp в миллисекундах
                    channel["last_post_time"] = int(create_at.timestamp() * 1000)
                elif isinstance(create_at, (int, float)):
                    # Если это уже timestamp
                    channel["last_post_time"] = int(create_at)
                else:
                    channel["last_post_time"] = 0
            else:
                channel["last_post"] = None
                channel["last_post_time"] = 0
            
            # Получаем количество непрочитанных сообщений
            unread_count = self.get_channel_unread_count(channel.get("id", ""))
            channel["unread_count"] = unread_count
            
            # Если нужно фильтровать только каналы с сообщениями
            if only_with_messages:
                if posts:
                    result_channels.append(channel)
            else:
                result_channels.append(channel)
        
        # Сортируем каналы по времени последнего сообщения (новые сверху)
        result_channels.sort(key=lambda x: x.get("last_post_time", 0), reverse=True)
        
        return result_channels

    def is_configured(self) -> bool:
        """
        Проверяет, настроен ли Mattermost для пользователя.
        
        Returns:
            True если настроен, False в противном случае
        """
        return bool(
            self.user_profile.mattermost_username and
            self.user_profile.mattermost_password and
            self.settings.server_url
        )

