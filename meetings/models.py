"""
Meetings app models - Meeting scheduling and management with CalDAV integration.
Optimized with proper indexing, relationships, and modern Django features.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import EmailValidator, MinLengthValidator
from django.utils import timezone
from datetime import timedelta


class MeetingStatus(models.TextChoices):
    """Meeting status choices."""
    DRAFT = 'draft', _('Черновик')
    SCHEDULED = 'scheduled', _('Запланирована')
    IN_PROGRESS = 'in_progress', _('Идет')
    COMPLETED = 'completed', _('Завершена')
    CANCELLED = 'cancelled', _('Отменена')


class MeetingRoom(models.Model):
    """Meeting room/Location model."""
    
    name = models.CharField(max_length=200, unique=True, verbose_name=_('Название'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    capacity = models.PositiveIntegerField(
        default=10,
        help_text=_('Максимальное количество участников'),
        verbose_name=_('Вместимость')
    )
    location = models.CharField(
        max_length=300,
        blank=True,
        verbose_name=_('Местоположение')
    )
    has_video_conf = models.BooleanField(
        default=True,
        verbose_name=_('Видеоконференция')
    )
    has_projector = models.BooleanField(
        default=False,
        verbose_name=_('Проектор')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Активна'))
    
    class Meta:
        ordering = ['name']
        verbose_name = _('Переговорная комната')
        verbose_name_plural = _('Переговорные комнаты')
        indexes = [
            models.Index(fields=['is_active', 'capacity']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.capacity} чел.)"


class Meeting(models.Model):
    """Meeting model for scheduling and tracking."""
    
    title = models.CharField(
        max_length=300,
        verbose_name=_('Название'),
        validators=[MinLengthValidator(3)]
    )
    description = models.TextField(verbose_name=_('Описание'))
    organizer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='organized_meetings',
        verbose_name=_('Организатор')
    )
    room = models.ForeignKey(
        MeetingRoom,
        on_delete=models.SET_NULL,
        null=True,
        related_name='meetings',
        verbose_name=_('Переговорная')
    )
    
    start_time = models.DateTimeField(verbose_name=_('Начало'))
    end_time = models.DateTimeField(verbose_name=_('Окончание'))
    
    status = models.CharField(
        max_length=20,
        choices=MeetingStatus.choices,
        default=MeetingStatus.DRAFT,
        verbose_name=_('Статус')
    )
    
    is_recurring = models.BooleanField(
        default=False,
        verbose_name=_('Повторяющаяся')
    )
    recurrence_pattern = models.CharField(
        max_length=20,
        blank=True,
        choices=[
            ('daily', 'Ежедневно'),
            ('weekly', 'Еженедельно'),
            ('monthly', 'Ежемесячно'),
        ],
        verbose_name=_('Паттерн повторения')
    )
    
    meeting_link = models.URLField(
        blank=True,
        help_text=_('Ссылка на видеоконференцию'),
        verbose_name=_('Ссылка на встречу')
    )
    
    caldav_uid = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('UID в CalDAV календаре'),
        verbose_name=_('CalDAV UID')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        ordering = ['-start_time']
        verbose_name = _('Встреча')
        verbose_name_plural = _('Встречи')
        indexes = [
            models.Index(fields=['status', 'start_time']),
            models.Index(fields=['organizer', '-start_time']),
            models.Index(fields=['start_time', 'end_time']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.start_time})"
    
    def clean(self):
        """Validate meeting times."""
        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                raise ValueError(_('Время окончания должно быть позже времени начала'))
    
    def is_upcoming(self):
        """Check if meeting is in the future."""
        return self.start_time > timezone.now()
    
    def is_current(self):
        """Check if meeting is currently happening."""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    def get_participants_count(self):
        """Get number of participants."""
        return self.participants.count()


class MeetingParticipant(models.Model):
    """Meeting participants with RSVP status."""
    
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='participants',
        verbose_name=_('Встреча')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_invitations',
        verbose_name=_('Участник')
    )
    email = models.EmailField(
        blank=True,
        help_text=_('Для внешних участников'),
        verbose_name=_('Email')
    )
    
    # RSVP status
    RESPONSE_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принято'),
        ('declined', 'Отклонено'),
        ('tentative', 'Возможно'),
    ]
    response = models.CharField(
        max_length=20,
        choices=RESPONSE_CHOICES,
        default='pending',
        verbose_name=_('Ответ')
    )
    
    joined_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Присоединился')
    )
    
    class Meta:
        unique_together = [['meeting', 'user'], ['meeting', 'email']]
        ordering = ['response']
        verbose_name = _('Участник встречи')
        verbose_name_plural = _('Участники встреч')
        indexes = [
            models.Index(fields=['meeting', 'response']),
            models.Index(fields=['user', 'response']),
        ]
    
    def __str__(self):
        name = self.user.get_full_name() if self.user else self.email
        return f"{name} - {self.get_response_display()}"


class MeetingAttachment(models.Model):
    """File attachments for meetings."""
    
    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Встреча')
    )
    file = models.FileField(upload_to='meeting_attachments/', verbose_name=_('Файл'))
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Загрузил')
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата загрузки'))
    
    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = _('Вложение')
        verbose_name_plural = _('Вложения')
        indexes = [
            models.Index(fields=['meeting', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.file.name} ({self.meeting.title})"
