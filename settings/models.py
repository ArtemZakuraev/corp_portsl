"""Settings app models - System configuration and user preferences."""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class SystemSetting(models.Model):
    """System-wide settings stored in database."""
    
    key = models.CharField(max_length=100, unique=True, verbose_name=_('Ключ'))
    value = models.TextField(verbose_name=_('Значение'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_settings',
        verbose_name=_('Обновил')
    )
    
    class Meta:
        ordering = ['key']
        verbose_name = _('Системная настройка')
        verbose_name_plural = _('Системные настройки')
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"
    
    @classmethod
    def get_value(cls, key, default=None):
        """Get setting value by key."""
        try:
            setting = cls.objects.get(key=key)
            return setting.value
        except cls.DoesNotExist:
            return default
    
    @classmethod
    def set_value(cls, key, value, description='', user=None):
        """Set or update setting value."""
        setting, created = cls.objects.update_or_create(
            key=key,
            defaults={
                'value': value,
                'description': description,
                'updated_by': user
            }
        )
        return setting


class MattermostProfile(models.Model):
    """User-specific Mattermost credentials and preferences."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mattermost_profile',
        verbose_name=_('Пользователь')
    )
    mm_username = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Имя пользователя Mattermost')
    )
    mm_password = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Пароль Mattermost')
    )
    mm_token = models.CharField(
        max_length=255,
        blank=True,
        help_text=_('Персональный токен доступа (альтернатива паролю)'),
        verbose_name=_('Токен доступа')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна интеграция')
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Последняя синхронизация')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))
    
    class Meta:
        ordering = ['user__username']
        verbose_name = _('Профиль Mattermost')
        verbose_name_plural = _('Профили Mattermost')
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['mm_username']),
        ]
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.user.username} ({self.mm_username or 'не настроено'})"
    
    @property
    def has_credentials(self):
        """Check if profile has valid credentials."""
        return bool(self.mm_username and (self.mm_password or self.mm_token))
    
    @classmethod
    def get_user_profile(cls, user):
        """Get or create Mattermost profile for user."""
        profile, _ = cls.objects.get_or_create(user=user)
        return profile
