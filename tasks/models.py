"""
Tasks app models - Task management and tracking.
Optimized with proper indexing, relationships, and modern Django features.
"""
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class TaskStatus(models.TextChoices):
    """Task status choices."""
    NEW = 'new', _('Новая')
    IN_PROGRESS = 'in_progress', _('В работе')
    REVIEW = 'review', _('На проверке')
    DONE = 'done', _('Завершена')
    CANCELLED = 'cancelled', _('Отменена')


class Priority(models.TextChoices):
    """Priority levels."""
    LOW = 'low', _('Низкий')
    MEDIUM = 'medium', _('Средний')
    HIGH = 'high', _('Высокий')
    CRITICAL = 'critical', _('Критический')


class Task(models.Model):
    """Task model for project management."""
    
    title = models.CharField(max_length=300, verbose_name=_('Название'))
    description = models.TextField(verbose_name=_('Описание'))
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_tasks',
        verbose_name=_('Автор')
    )
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name=_('Исполнитель')
    )
    status = models.CharField(
        max_length=20,
        choices=TaskStatus.choices,
        default=TaskStatus.NEW,
        verbose_name=_('Статус')
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name=_('Приоритет')
    )
    due_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Срок выполнения')
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Дата завершения')
    )
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name=_('Родительская задача')
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text=_('Теги через запятую'),
        verbose_name=_('Теги')
    )
    progress = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_('Прогресс (%)')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        ordering = ['-priority', '-created_at']
        verbose_name = _('Задача')
        verbose_name_plural = _('Задачи')
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['assignee', 'status']),
            models.Index(fields=['due_date']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Check if task is overdue."""
        if self.due_date and self.status != TaskStatus.DONE:
            return timezone.now() > self.due_date
        return False
    
    def complete(self):
        """Mark task as completed."""
        self.status = TaskStatus.DONE
        self.completed_at = timezone.now()
        self.progress = 100
        self.save(update_fields=['status', 'completed_at', 'progress'])


class TaskComment(models.Model):
    """Comments on tasks."""
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('Задача')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_comments',
        verbose_name=_('Автор')
    )
    content = models.TextField(verbose_name=_('Комментарий'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class TaskAttachment(models.Model):
    """File attachments for tasks."""
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name=_('Задача')
    )
    file = models.FileField(upload_to='task_attachments/', verbose_name=_('Файл'))
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
            models.Index(fields=['task', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.file.name} ({self.task.title})"
