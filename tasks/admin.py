"""Tasks app admin configuration."""
from django.contrib import admin
from .models import Task, TaskComment, TaskAttachment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'assignee', 'status', 'priority', 'due_date', 'created_at')
    list_filter = ('status', 'priority', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'tags')
    raw_id_fields = ('author', 'assignee', 'parent_task')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')
    list_filter = ('created_at',)
    raw_id_fields = ('task', 'author')
    date_hierarchy = 'created_at'


@admin.register(TaskAttachment)
class TaskAttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    raw_id_fields = ('task', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
