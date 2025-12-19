import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse


class WikiViewGroup(models.Model):
    """
    Группа просмотра для статей базы знаний.
    Позволяет ограничить доступ к статьям определенным группам пользователей.
    """
    
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название группы",
        help_text="Уникальное название группы просмотра."
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Описание группы и её назначения."
    )
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='wiki_view_groups',
        blank=True,
        verbose_name="Пользователи",
        help_text="Пользователи, входящие в эту группу просмотра."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    
    class Meta:
        verbose_name = "Группа просмотра"
        verbose_name_plural = "Группы просмотра"
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name


class WikiArticle(models.Model):
    """
    Статья базы знаний.
    Поддерживает иерархическую структуру (вложенные статьи).
    """
    
    VISIBILITY_ALL = 'all'
    VISIBILITY_REGISTERED = 'registered'
    VISIBILITY_GROUPS = 'groups'
    
    VISIBILITY_CHOICES = [
        (VISIBILITY_ALL, 'Все (включая неавторизованных)'),
        (VISIBILITY_REGISTERED, 'Только зарегистрированные пользователи'),
        (VISIBILITY_GROUPS, 'Пользователи групп'),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name="Название статьи",
        help_text="Краткое название статьи, которое будет отображаться в содержании."
    )
    slug = models.SlugField(
        max_length=255,
        unique=True,
        editable=False,
        verbose_name="URL-адрес",
        help_text="Уникальный идентификатор для URL статьи (генерируется автоматически)."
    )
    content = models.TextField(
        verbose_name="Содержание статьи",
        help_text="Основной текст статьи. Поддерживается HTML-разметка для форматирования."
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name="Родительская статья",
        help_text="Выберите родительскую статью, если эта статья является подразделом другой статьи."
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name="Порядок отображения",
        help_text="Число для сортировки статей в содержании (меньше = выше в списке)."
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wiki_articles',
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Если снято, статья не будет отображаться в содержании."
    )
    visibility_type = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default=VISIBILITY_REGISTERED,
        verbose_name="Кто может видеть статью",
        help_text="Выберите, кто имеет доступ к просмотру этой статьи."
    )
    view_groups = models.ManyToManyField(
        WikiViewGroup,
        related_name='articles',
        blank=True,
        verbose_name="Группы просмотра",
        help_text="Выберите группы пользователей, которые могут видеть эту статью (используется при выборе 'Пользователи групп')."
    )
    
    class Meta:
        verbose_name = "Статья базы знаний"
        verbose_name_plural = "Статьи базы знаний"
        ordering = ['order', 'title']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['parent', 'order']),
        ]
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        """Автоматически генерируем slug из UUID, если он не задан."""
        if not self.slug:
            # Генерируем уникальный slug из UUID
            self.slug = str(uuid.uuid4()).replace('-', '')[:32]
            # Проверяем уникальность
            while WikiArticle.objects.filter(slug=self.slug).exists():
                self.slug = str(uuid.uuid4()).replace('-', '')[:32]
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('wiki_article', kwargs={'slug': self.slug})
    
    def can_view(self, user):
        """
        Проверяет, может ли пользователь просматривать эту статью.
        user может быть AnonymousUser для неавторизованных пользователей.
        """
        if not self.is_published:
            return False
        
        # Все могут видеть, если выбрано "Все"
        if self.visibility_type == self.VISIBILITY_ALL:
            return True
        
        # Для остальных типов нужна авторизация
        if not hasattr(user, 'is_authenticated') or not user.is_authenticated:
            return False
        
        # Зарегистрированные пользователи могут видеть
        if self.visibility_type == self.VISIBILITY_REGISTERED:
            return True
        
        # Проверяем группы
        if self.visibility_type == self.VISIBILITY_GROUPS:
            # Проверяем, входит ли пользователь хотя бы в одну из групп
            return self.view_groups.filter(users=user).exists()
        
        return False
    
    def get_breadcrumbs(self):
        """Возвращает список родительских статей для хлебных крошек."""
        breadcrumbs = []
        current = self.parent
        while current:
            breadcrumbs.insert(0, current)
            current = current.parent
        return breadcrumbs
    
    def get_all_children(self):
        """Возвращает все дочерние статьи (рекурсивно)."""
        children = list(self.children.filter(is_published=True))
        for child in children:
            children.extend(child.get_all_children())
        return children


class WikiImage(models.Model):
    """
    Изображение, прикреплённое к статье базы знаний.
    """
    
    article = models.ForeignKey(
        WikiArticle,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Статья",
    )
    image = models.ImageField(
        upload_to='wiki/images/',
        verbose_name="Изображение",
        help_text="Загрузите изображение в формате JPG, PNG, GIF или WebP.",
    )
    alt_text = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Альтернативный текст",
        help_text="Описание изображения для доступности (alt-текст).",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )
    
    class Meta:
        verbose_name = "Изображение статьи"
        verbose_name_plural = "Изображения статей"
        ordering = ['uploaded_at']
    
    def __str__(self) -> str:
        return f"Изображение для {self.article.title}"


class WikiFile(models.Model):
    """
    Файл, прикреплённый к статье базы знаний.
    """
    
    article = models.ForeignKey(
        WikiArticle,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Статья",
    )
    file = models.FileField(
        upload_to='wiki/files/',
        verbose_name="Файл",
        help_text="Загрузите файл для прикрепления к статье.",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Название файла",
        help_text="Отображаемое название файла (по умолчанию используется имя файла).",
        blank=True,
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание",
        help_text="Краткое описание файла.",
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата загрузки"
    )
    
    class Meta:
        verbose_name = "Файл статьи"
        verbose_name_plural = "Файлы статей"
        ordering = ['uploaded_at']
    
    def __str__(self) -> str:
        return self.name or self.file.name
    
    def get_file_name(self):
        """Возвращает название файла для отображения."""
        return self.name or self.file.name.split('/')[-1]

