import uuid

from django.conf import settings
from django.db import models


class Invitation(models.Model):
    """
    Пригласительная ссылка для регистрации пользователя в портале.
    Генерируется администратором, содержит токен и срок действия.
    """

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_invitations",
        verbose_name="Создано пользователем",
    )

    used_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="used_invitations",
        verbose_name="Использовано пользователем",
    )
    used_at = models.DateTimeField(null=True, blank=True)

    email_hint = models.EmailField(
        null=True,
        blank=True,
        verbose_name="Рекомендуемый email",
        help_text="Необязательно. Можно указать, если приглашение предназначено для конкретного человека.",
    )

    class Meta:
        verbose_name = "Пригласительная ссылка"
        verbose_name_plural = "Пригласительные ссылки"

    def __str__(self) -> str:  # type: ignore[override]
        return f"Приглашение {self.token}"

    @property
    def is_expired(self) -> bool:
        from django.utils import timezone

        return self.expires_at < timezone.now()


class UserProfile(models.Model):
    """
    Расширенные личные данные пользователя и его орг.привязка.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")

    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=True)
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=True)
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=True)

    department = models.ForeignKey(
        "organization.Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_employees",
        verbose_name="Департамент",
        help_text="Выберите департамент из списка департаментов.",
    )
    unit = models.ForeignKey(
        "organization.Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_employees",
        verbose_name="Отдел",
        help_text="Выберите отдел из списка отделов.",
    )
    position = models.ForeignKey(
        "organization.Position",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profile_employees",
        verbose_name="Должность",
        help_text="Выберите должность из справочника должностей.",
    )

    phone_personal = models.CharField(max_length=50, verbose_name="Личный телефон", blank=True)
    phone_internal = models.CharField(max_length=20, verbose_name="Внутренний телефон", blank=True)

    photo = models.ImageField(
        upload_to="portal/",
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Загрузите фото в формате JPG, PNG или GIF.",
    )

    manager = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="managed_employees",
        verbose_name="Руководитель",
        null=True,
        blank=True,
        help_text="Выберите руководителя из списка сотрудников портала.",
    )

    is_news_moderator = models.BooleanField(
        default=False,
        verbose_name="Модератор новостей",
        help_text="Если отмечено, пользователь может создавать и публиковать корпоративные новости.",
    )
    is_wiki_moderator = models.BooleanField(
        default=False,
        verbose_name="Модератор базы знаний",
        help_text="Если отмечено, пользователь может создавать и редактировать статьи базы знаний.",
    )

    # Настройки персональной темы оформления
    THEME_MODE_CHOICES = [
        ("default", "Стиль системы по умолчанию"),
        ("light", "Светлая тема"),
        ("dark", "Тёмная тема"),
        ("custom", "Пользовательские цвета"),
    ]

    theme_mode = models.CharField(
        max_length=20,
        choices=THEME_MODE_CHOICES,
        default="default",
        verbose_name="Режим темы",
    )
    theme_primary_color = models.CharField(
        max_length=7,
        verbose_name="Основной цвет акцента",
        blank=True,
        help_text="HEX, например #ffd94a. Используется при режиме \"Пользовательские цвета\".",
    )
    theme_sidebar_bg_color = models.CharField(
        max_length=7,
        verbose_name="Цвет фона меню",
        blank=True,
        help_text="HEX-цвет фона бокового меню.",
    )
    theme_header_bg_color = models.CharField(
        max_length=7,
        verbose_name="Цвет шапки",
        blank=True,
        help_text="HEX-цвет фона верхней панели.",
    )

    # Настройки Mattermost
    mattermost_username = models.CharField(
        max_length=255,
        verbose_name="Логин Mattermost",
        blank=True,
        help_text="Логин для авторизации на сервере Mattermost.",
    )
    mattermost_password = models.CharField(
        max_length=255,
        verbose_name="Пароль Mattermost",
        blank=True,
        help_text="Пароль для авторизации на сервере Mattermost. Хранится в открытом виде.",
    )

    # Настройки CalDAV
    caldav_email = models.EmailField(
        max_length=255,
        verbose_name="Email для CalDAV",
        blank=True,
        help_text="Email для подключения к серверу CalDAV. Используется для формирования URL календаря.",
    )
    caldav_password = models.CharField(
        max_length=255,
        verbose_name="Пароль CalDAV",
        blank=True,
        help_text="Пароль для подключения к серверу CalDAV. Хранится в открытом виде.",
    )

    # Настройки ленты (порядок блоков)
    dashboard_blocks_order = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Порядок блоков на ленте",
        help_text="JSON-массив с идентификаторами блоков в порядке их отображения.",
    )

    # Настройки цветов важности задач
    task_priority_important_color = models.CharField(
        max_length=7,
        default="#4CAF50",
        verbose_name="Цвет для важных задач",
        help_text="HEX-цвет для задач с важностью 'Важно' (по умолчанию: #4CAF50).",
    )
    task_priority_urgent_color = models.CharField(
        max_length=7,
        default="#FF9800",
        verbose_name="Цвет для срочных задач",
        help_text="HEX-цвет для задач с важностью 'Срочно' (по умолчанию: #FF9800).",
    )
    task_priority_critical_color = models.CharField(
        max_length=7,
        default="#F44336",
        verbose_name="Цвет для критичных задач",
        help_text="HEX-цвет для задач с важностью 'Критично' (по умолчанию: #F44336).",
    )

    # Настройки отображения задач
    task_view_mode = models.CharField(
        max_length=20,
        choices=[
            ("list", "Список"),
            ("kanban", "Канбан-доска"),
        ],
        default="list",
        verbose_name="Режим отображения задач",
        help_text="Выберите способ отображения списка задач.",
    )
    task_sort_by = models.CharField(
        max_length=20,
        choices=[
            ("priority", "По важности"),
            ("due_date", "По дате окончания"),
            ("created_at", "По дате создания"),
        ],
        default="due_date",
        verbose_name="Сортировка задач",
        help_text="Выберите способ сортировки задач.",
    )

    # Настройки сайдбара (левого меню)
    sidebar_custom_enabled = models.BooleanField(
        default=False,
        verbose_name="Включить настройку сайдбара",
        help_text="Включите, чтобы настроить ширину и высоту левого меню под свой экран.",
    )
    sidebar_width = models.PositiveIntegerField(
        default=280,
        verbose_name="Ширина сайдбара (px)",
        help_text="Ширина левого меню в пикселях (по умолчанию: 280px).",
    )
    sidebar_height = models.CharField(
        max_length=50,
        default="calc(100vh - 64px)",
        verbose_name="Высота сайдбара",
        help_text="Высота левого меню. Можно указать в пикселях (например: 600px) или использовать calc (например: calc(100vh - 64px)).",
    )

    # Настройки меню (JSON для хранения порядка, видимости, избранного)
    menu_items_settings = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Настройки пунктов меню",
        help_text="JSON с настройками пунктов меню: порядок, видимость, избранное.",
    )
    menu_show_favorites_only = models.BooleanField(
        default=False,
        verbose_name="Показывать только избранное",
        help_text="Если включено, в меню отображаются только избранные пункты.",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:  # type: ignore[override]
        return f"Профиль {self.user.username}"
