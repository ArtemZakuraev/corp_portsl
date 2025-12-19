from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class PortalSettings(models.Model):
    """
    Настройки оформления портала.
    Администратор может загрузить логотип и favicon.
    Предполагается, что в системе существует только одна запись.
    """

    site_name = models.CharField(
        max_length=255,
        default="Корпоративный портал",
        verbose_name="Название портала",
    )
    logo = models.ImageField(
        upload_to="portal/",
        blank=True,
        null=True,
        verbose_name="Логотип",
        help_text="Рекомендуется загружать изображение в формате PNG с прозрачным фоном.",
    )
    favicon = models.ImageField(
        upload_to="portal/",
        blank=True,
        null=True,
        verbose_name="Favicon",
        help_text="Иконка сайта (обычно квадратное изображение 32x32 или 64x64).",
    )

    STORAGE_LOCAL = "local"
    STORAGE_S3 = "s3"

    DOCUMENT_STORAGE_CHOICES = [
        (STORAGE_LOCAL, "Локальный диск (внутреннее хранилище)"),
        (STORAGE_S3, "S3-совместимое хранилище"),
    ]

    document_storage_type = models.CharField(
        max_length=20,
        choices=DOCUMENT_STORAGE_CHOICES,
        default=STORAGE_LOCAL,
        verbose_name="Тип хранилища документов",
        help_text="Выберите, где хранить файлы документов: на локальном диске или во внешнем S3-совместимом хранилище.",
    )

    s3_endpoint_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="S3 Endpoint URL",
        help_text="Адрес S3-совместимого хранилища (например, https://s3.example.com). Используется, если выбран тип S3.",
    )
    s3_access_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="S3 Access Key",
    )
    s3_secret_key = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="S3 Secret Key",
    )
    s3_bucket_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="S3 Bucket",
    )

    class Meta:
        verbose_name = "Настройки портала"
        verbose_name_plural = "Настройки портала"

    def __str__(self) -> str:  # type: ignore[override]
        return self.site_name

    @classmethod
    def get_solo(cls) -> "PortalSettings":
        """
        Возвращает единственный экземпляр настроек.
        Если его нет — создаёт с настройками по умолчанию.
        """
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class MailServerSettings(models.Model):
    """
    Настройки почтового сервера для портала.
    Используются для отправки писем (приглашения, уведомления и т.п.).
    """

    host = models.CharField(max_length=255, verbose_name="SMTP хост", default="smtp.example.com")
    port = models.PositiveIntegerField(verbose_name="SMTP порт", default=587)
    use_tls = models.BooleanField(verbose_name="Использовать TLS", default=True)
    use_ssl = models.BooleanField(verbose_name="Использовать SSL", default=False)
    username = models.CharField(max_length=255, verbose_name="Имя пользователя", blank=True, null=True)
    password = models.CharField(max_length=255, verbose_name="Пароль", blank=True, null=True)
    from_email = models.EmailField(
        verbose_name="Email отправителя",
        default="no-reply@example.com",
    )

    class Meta:
        verbose_name = "Настройки почтового сервера"
        verbose_name_plural = "Настройки почтового сервера"

    def __str__(self) -> str:  # type: ignore[override]
        return f"SMTP {self.host}:{self.port}"

    @classmethod
    def get_solo(cls) -> "MailServerSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CaldavSettings(models.Model):
    """
    Настройки подключения к CalDAV-серверу для работы с календарями встреч.
    Задаётся общий сервер. Авторизация происходит через настройки каждого пользователя.
    URL календаря формируется по шаблону: $server/SOGo/dav/$user_email/Calendar/personal/
    где $server - это server_url, а $user_email берется из настроек пользователя.
    """

    server_url = models.URLField(
        verbose_name="URL CalDAV сервера",
        help_text="Базовый URL сервера CalDAV (например: https://caldav.example.com). Email и пароль настраиваются в профиле пользователя.",
    )

    class Meta:
        verbose_name = "Настройки CalDAV"
        verbose_name_plural = "Настройки CalDAV"

    def __str__(self) -> str:  # type: ignore[override]
        return self.server_url

    @classmethod
    def get_solo(cls) -> "CaldavSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class MattermostSettings(models.Model):
    """
    Настройки подключения к серверу Mattermost для работы с корпоративными чатами.
    """

    server_url = models.URLField(
        verbose_name="URL сервера Mattermost",
        help_text="Например: https://mattermost.example.com",
    )
    api_version = models.CharField(
        max_length=20,
        default="v4",
        verbose_name="Версия API",
        help_text="Версия Mattermost API (обычно v4).",
    )
    verify_ssl = models.BooleanField(
        default=True,
        verbose_name="Проверять SSL сертификат",
        help_text="Отключите, если используется самоподписанный сертификат. Не рекомендуется для production.",
    )

    class Meta:
        verbose_name = "Настройки Mattermost"
        verbose_name_plural = "Настройки Mattermost"

    def __str__(self) -> str:  # type: ignore[override]
        return f"Mattermost {self.server_url}"

    @classmethod
    def get_solo(cls) -> "MattermostSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class VacationRequest(models.Model):
    """
    Заявка / запись в графике отпусков для конкретного сотрудника.
    Дублируем ключевые поля (ФИО, отдел, должность) для фиксации состояния на момент заполнения.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # type: ignore[name-defined]
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacation_requests",
        verbose_name="Пользователь",
    )
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacation_requests",
        verbose_name="Департамент",
    )
    unit = models.ForeignKey(
        "Unit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacation_requests",
        verbose_name="Отдел",
    )
    position = models.ForeignKey(
        "Position",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="vacation_requests",
        verbose_name="Должность",
    )
    last_name = models.CharField(max_length=150, verbose_name="Фамилия")
    first_name = models.CharField(max_length=150, verbose_name="Имя")
    middle_name = models.CharField(max_length=150, verbose_name="Отчество")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        verbose_name = "График отпусков (заявка)"
        verbose_name_plural = "Графики отпусков (заявки)"

    def __str__(self) -> str:  # type: ignore[override]
        return f"График отпусков {self.last_name} {self.first_name}"


class VacationPeriod(models.Model):
    """
    Отдельный период отпуска в рамках заявки.
    """

    TYPE_CHOICES = [
        ("main", "Основной отпуск"),
        ("extra", "Дополнительный отпуск"),
    ]

    request = models.ForeignKey(
        VacationRequest,
        on_delete=models.CASCADE,
        related_name="periods",
        verbose_name="График отпусков",
    )
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    vacation_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="main",
        verbose_name="Тип отпуска",
    )

    class Meta:
        verbose_name = "Период отпуска"
        verbose_name_plural = "Периоды отпусков"

    def get_days_count(self) -> int:
        """Возвращает количество дней отпуска (включая начальный и конечный день)."""
        if self.start_date and self.end_date:
            delta = self.end_date - self.start_date
            return delta.days + 1  # +1 чтобы включить оба дня
        return 0

    @staticmethod
    def get_user_vacation_days_for_year(user, year: int) -> int:
        """
        Подсчитывает общее количество дней отпуска для пользователя за указанный год.
        Учитываются только периоды отпусков, которые попадают в указанный год.
        """
        from django.db.models import Q
        from datetime import date
        
        # Получаем все периоды отпусков пользователя, которые пересекаются с указанным годом
        # Период пересекается с годом, если:
        # - начинается до конца года И заканчивается после начала года
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        
        periods = VacationPeriod.objects.filter(
            request__user=user
        ).filter(
            Q(start_date__lte=year_end) & Q(end_date__gte=year_start)
        )
        
        total_days = 0
        
        for period in periods:
            # Определяем фактический период в рамках года
            period_start = max(period.start_date, year_start)
            period_end = min(period.end_date, year_end)
            
            if period_start <= period_end:
                delta = period_end - period_start
                total_days += delta.days + 1  # +1 чтобы включить оба дня
        
        return total_days


class Position(models.Model):
    """
    Справочник должностей компании.
    """
    
    name = models.CharField(
        max_length=255,
        verbose_name="Название должности",
        unique=True,
        help_text="Например: Менеджер по продажам, Разработчик, Директор и т.д.",
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ["name"]
    
    def __str__(self) -> str:  # type: ignore[override]
        return self.name


class Department(models.Model):
    """
    Департамент компании.
    Может включать в себя несколько отделов и быть подчинён другому департаменту.
    """

    name = models.CharField(max_length=255, verbose_name="Название департамента", unique=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_departments",
        verbose_name="Руководитель департамента",
        help_text="Выберите руководителя из таблицы руководителей департаментов.",
    )
    department_head = models.ForeignKey(
        "DepartmentHead",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
        verbose_name="Руководитель департамента (из таблицы)",
        help_text="Выберите руководителя из таблицы руководителей департаментов.",
    )
    parent_department = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sub_departments",
        verbose_name="Родительский департамент",
        help_text="Выберите департамент, которому подчинён данный департамент.",
    )
    units = models.ManyToManyField(
        "Unit",
        related_name="departments",
        blank=True,
        verbose_name="Отделы департамента",
        help_text="Отделы, входящие в этот департамент.",
    )

    class Meta:
        verbose_name = "Департамент"
        verbose_name_plural = "Департаменты"

    def __str__(self) -> str:  # type: ignore[override]
        return self.name


class Unit(models.Model):
    """
    Отдел внутри компании.
    Может входить в несколько департаментов и содержать список сотрудников.
    """

    name = models.CharField(max_length=255, verbose_name="Название отдела", unique=True)
    head = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="headed_units",
        verbose_name="Руководитель отдела",
        help_text="Выберите руководителя из таблицы руководителей отделов.",
    )
    unit_head = models.ForeignKey(
        "UnitHead",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="units",
        verbose_name="Руководитель отдела (из таблицы)",
        help_text="Выберите руководителя из таблицы руководителей отделов.",
    )
    employees = models.ManyToManyField(
        User,
        related_name="units_memberships",
        blank=True,
        verbose_name="Сотрудники отдела",
        help_text="Сотрудники, входящие в этот отдел.",
    )

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"

    def __str__(self) -> str:  # type: ignore[override]
        return self.name


class DepartmentHead(models.Model):
    """
    Руководитель департамента.
    Содержит все данные сотрудника из UserProfile плюс наименование департамента, которым он руководит.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="department_heads",
        verbose_name="Сотрудник",
    )
    
    # Данные сотрудника из UserProfile
    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=True)
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=True)
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=True)
    
    department = models.CharField(max_length=255, verbose_name="Департамент", blank=True)
    unit = models.CharField(max_length=255, verbose_name="Отдел", blank=True)
    position = models.CharField(max_length=255, verbose_name="Должность", blank=True)
    
    phone_personal = models.CharField(max_length=50, verbose_name="Личный телефон", blank=True)
    phone_internal = models.CharField(max_length=20, verbose_name="Внутренний телефон", blank=True)
    
    photo = models.ImageField(
        upload_to="portal/",
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Загрузите фото в формате JPG, PNG или GIF.",
    )
    
    # Наименование департамента, которым руководит
    department_name = models.CharField(
        max_length=255,
        verbose_name="Наименование департамента",
        help_text="Название департамента, которым руководит данный сотрудник.",
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Руководитель департамента"
        verbose_name_plural = "Руководители департаментов"
        unique_together = [["user", "department_name"]]

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.last_name} {self.first_name} - {self.department_name}"


class UnitHead(models.Model):
    """
    Руководитель отдела.
    Содержит все данные сотрудника из UserProfile плюс наименование отдела, которым он руководит.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="unit_heads",
        verbose_name="Сотрудник",
    )
    
    # Данные сотрудника из UserProfile
    last_name = models.CharField(max_length=150, verbose_name="Фамилия", blank=True)
    first_name = models.CharField(max_length=150, verbose_name="Имя", blank=True)
    middle_name = models.CharField(max_length=150, verbose_name="Отчество", blank=True)
    
    department = models.CharField(max_length=255, verbose_name="Департамент", blank=True)
    unit = models.CharField(max_length=255, verbose_name="Отдел", blank=True)
    position = models.CharField(max_length=255, verbose_name="Должность", blank=True)
    
    phone_personal = models.CharField(max_length=50, verbose_name="Личный телефон", blank=True)
    phone_internal = models.CharField(max_length=20, verbose_name="Внутренний телефон", blank=True)
    
    photo = models.ImageField(
        upload_to="portal/",
        blank=True,
        null=True,
        verbose_name="Фотография",
        help_text="Загрузите фото в формате JPG, PNG или GIF.",
    )
    
    # Наименование отдела, которым руководит
    unit_name = models.CharField(
        max_length=255,
        verbose_name="Наименование отдела",
        help_text="Название отдела, которым руководит данный сотрудник.",
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Руководитель отдела"
        verbose_name_plural = "Руководители отделов"
        unique_together = [["user", "unit_name"]]

    def __str__(self) -> str:  # type: ignore[override]
        return f"{self.last_name} {self.first_name} - {self.unit_name}"
