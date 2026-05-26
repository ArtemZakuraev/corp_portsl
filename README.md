# Корпоративный портал (Corporate Portal)

[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)

Современный корпоративный портал с интеграцией Mattermost, CalDAV и OnlyOffice для управления сотрудниками, задачами, встречами, новостями и базой знаний.

## Оглавление

- [Возможности](#-возможности)
- [Архитектура системы](#-архитектура-системы)
- [Установка и запуск](#-установка-и-запуск)
- [Конфигурация](#-конфигурация)
- [Модули системы](#-модули-системы)
- [API и интеграции](#-api-и-интеграции)
- [Технологический стек](#-технологический-стек)
- [Структура проекта](#-структура-проекта)

---

## Возможности

### Основной функционал
- **Интеграция с Mattermost** — современный веб-клиент с красивым UI, отправкой сообщений, мониторингом и статистикой
- **Организационная структура** — схема подчинённости на основе справочника сотрудников, отделов и департаментов
- **Планирование отпусков** — учёт отсутствий сотрудников
- **Wiki** — база знаний с версиями статей и категориями
- **Система новостей** — публикации с рассылкой на почту и уведомлениями в Mattermost
- **Задачи** — полноценное управление задачами с приоритетами, статусами и дедлайнами
- **Встречи** — планирование встреч с интеграцией CalDAV календаря и бронированием переговорных

### Дополнительные возможности
- Интеграция с почтовым сервером для задач и встреч
- Интеграция с OnlyOffice для редактирования документов
- Адаптивный glassmorphism дизайн
- Система уведомлений через email и Mattermost

---

## Архитектура системы

```
┌─────────────────────────────────────────────────────────────┐
│                 Корпоративный портал                        │
├─────────────────────────────────────────────────────────────┤
│  Employees  │  News  │  Tasks  │  Meetings  │  Wiki        │
│  (Django Models + ORM + Relationships)                      │
├─────────────────────────────────────────────────────────────┤
│              PostgreSQL Database                            │
│        (Persistent Connections + Caching)                   │
├─────────────────────────────────────────────────────────────┤
│         External Services Integration                       │
│  Mattermost (Chat)  │  CalDAV (Calendar)  │  OnlyOffice    │
└─────────────────────────────────────────────────────────────┘
```

---

## Установка и запуск

### Быстрый старт с Docker

```bash
# Генерация SSL сертификатов (для OnlyOffice)
docker-compose --profile cert run --rm cert_generator

# Запуск всех сервисов
docker-compose up -d

# Применение миграций
docker-compose exec web python manage.py migrate

# Создание суперпользователя
docker-compose exec web python manage.py createsuperuser
```

### Ручная установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Применение миграций
python manage.py migrate

# Создание суперпользователя
python manage.py createsuperuser

# Запуск сервера
python manage.py runserver
```

---

## Конфигурация

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `DJANGO_SECRET_KEY` | Секретный ключ Django | Автогенерация |
| `DJANGO_DEBUG` | Режим отладки | `False` |
| `POSTGRES_DB` | Имя базы данных | `corp_portal` |
| `POSTGRES_USER` | Пользователь БД | `corp_portal` |
| `POSTGRES_PASSWORD` | Пароль БД | `corp_portal` |
| `POSTGRES_HOST` | Хост БД | `db` |
| `MATTERMOST_URL` | URL Mattermost сервера | - |
| `MATTERMOST_TOKEN` | Токен API Mattermost | - |
| `MATTERMOST_WEBHOOK_URL` | URL вебхука Mattermost | - |
| `EMAIL_HOST` | SMTP сервер | - |
| `ONLYOFFICE_URL` | URL OnlyOffice | `http://onlyoffice:80` |

---

## Модули системы

### Сотрудники и организационная структура

**Модели:** Department, Position, Employee

**Функционал:**
- Иерархическая структура отделов (дерево подчинённости)
- Карточки сотрудников с аватарами и контактами
- Визуализация организационной структуры
- Поиск и фильтрация сотрудников

**URL:** `/dashboard/`, `/employees/`

---

### Новости

**Модели:** NewsCategory, News

**Функционал:**
- Публикация новостей с категориями
- Закреплённые новости
- Счётчик просмотров
- Email-рассылка новых новостей
- Уведомления в Mattermost

**URL:** `/news/`

---

### Задачи

**Модели:** Task, TaskComment, TaskAttachment

**Статусы задач:** new, in_progress, review, done, cancelled

**Приоритеты:** low, medium, high, critical

**Функционал:**
- Создание и назначение задач
- Подзадачи (иерархия)
- Прогресс выполнения (0-100%)
- Дедлайны и напоминания
- Уведомления в Mattermost

**URL:** `/tasks/`

---

### Встречи

**Модели:** MeetingRoom, Meeting, MeetingParticipant

**Функционал:**
- Бронирование переговорных комнат
- Приглашение участников (RSVP)
- Повторяющиеся встречи
- Синхронизация с CalDAV календарём
- Напоминания в Mattermost

**URL:** `/meetings/`

---

### Wiki (База знаний)

**Модели:** WikiCategory, WikiArticle

**Функционал:**
- Иерархия категорий
- Версионирование статей
- Избранные статьи
- Счётчик просмотров
- Вложения (файлы)

**URL:** `/wiki/`

---

### Mattermost Интеграция

**Современный интерфейс v2.0:**

**Компоненты:**
- `MattermostClient` — высокопроизводительный клиент
- `MattermostConfig` — конфигурация
- `MattermostMessage` — журнал сообщений

**Функционал:**
- **Dashboard** — панель управления со статистикой
- **Отправка сообщений** — удобный интерфейс с Markdown
- **Журнал сообщений** — лог с фильтрацией и поиском
- **Тест соединения** — проверка подключения в реальном времени

**Производительность:**
- Connection pooling (10 соединений, 20 максимальных)
- Retry logic (3 попытки с backoff)
- Кэширование для предотвращения дубликатов

**URL:** `/mattermost/`

**Примеры использования:**

```python
from mattermost_integration import get_mattermost_client

client = get_mattermost_client()

# Отправка сообщения
client.send_message("Привет, команда!", channel="general")

# Уведомление пользователю
client.send_to_user(user, "Вам назначена новая задача")

# Уведомление о новости
client.send_news_notification(news_item)

# Тест соединения
result = client.test_connection()
print(f"Status: {result['success']}, Time: {result['response_time_ms']}ms")
```

---

## API и интеграции

### Внешние интеграции

#### Mattermost
- Outgoing webhooks для уведомлений
- Incoming webhooks для команд
- Bot integration для автоматизации

#### CalDAV
- Синхронизация календаря встреч
- Импорт событий из почтового сервера

#### OnlyOffice
- Редактирование документов онлайн
- Совместная работа над файлами

---

## Технологический стек

### Backend
- **Django 5.0** — веб-фреймворк
- **PostgreSQL 16** — база данных
- **psycopg2-binary** — драйвер БД
- **argon2-cffi** — хеширование паролей
- **caldav** — интеграция календарей
- **requests** — HTTP-клиент
- **Pillow** — обработка изображений

### Frontend
- **HTML5/CSS3** — семантическая вёрстка
- **Glassmorphism UI** — современный дизайн
- **Vanilla JavaScript** — интерактивность
- **Google Fonts (Inter)** — типографика
- **SVG Icons** — векторная графика

### DevOps
- **Docker** — контейнеризация
- **Docker Compose** — оркестрация
- **Nginx** — reverse proxy

---

## Структура проекта

```
corp_portal/
├── corp_portal/          # Основной проект Django
│   ├── settings.py       # Настройки проекта
│   ├── urls.py           # Корневые URL
│   └── wsgi.py           # WSGI конфиг
├── employees/            # Модуль сотрудников
├── news/                 # Модуль новостей
├── tasks/                # Модуль задач
├── meetings/             # Модуль встреч
├── wiki/                 # Модуль базы знаний
├── mattermost_integration/  # Интеграция Mattermost
├── templates/            # HTML шаблоны
├── static/               # Статические файлы (CSS, JS, images)
├── media/                # Медиафайлы пользователей
├── manage.py             # Управление Django
├── requirements.txt      # Зависимости Python
├── docker-compose.yml    # Docker конфигурация
└── README.md             # Документация
```

---

##  Производительность

### Оптимизации

1. **Database**
   - Persistent connections (CONN_MAX_AGE=600)
   - Health checks для соединений
   - Индексы на часто используемых полях
   - select_related и prefetch_related

2. **Caching**
   - LocMemCache для частых операций
   - Кэширование дубликатов сообщений Mattermost

3. **Connection Pooling**
   - HTTP session reuse для Mattermost
   - Retry logic с exponential backoff
   - Max 20 одновременных соединений

4. **Frontend**
   - CSS variables для быстрой смены тем
   - Minimal repaints с GPU acceleration
   - Preconnect к Google Fonts

---

##  Безопасность

### Реализованные меры безопасности

1. **Аутентификация**
   - Argon2 хеширование паролей
   - CSRF защита на всех формах
   - Session security cookies

2. **Авторизация**
   - Login required декораторы
   - Проверка прав доступа

3. **Защита данных**
   - SQL injection prevention (ORM)
   - XSS protection (auto-escaping)
   - Clickjacking protection (X-Frame-Options)

4. **Production настройки**
   - SECURE_SSL_REDIRECT
   - HSTS (HTTP Strict Transport Security)
   - Secure cookies

---

##  Мониторинг и логи

### Логирование

```python
import logging
logger = logging.getLogger(__name__)

# Логирование ошибок Mattermost
logger.error(f"Mattermost API error: {response.status_code}")

# Логирование вебхуков
logger.info(f"Mattermost webhook received: {data}")
```

### Health Checks

- PostgreSQL health check каждые 5 секунд
- Mattermost connection test через UI
- Docker container health checks

---

##  Тестирование

```bash
# Запуск тестов
python manage.py test

# Линтинг
flake8 .
pylint */
```

---

##  Лицензия

MIT License

---

##  Команда

Разработано командой **Corporate Portal Team**.

---

*Последнее обновление: 2024*
