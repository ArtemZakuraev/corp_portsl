"""Meetings app admin configuration."""
from django.contrib import admin
from .models import Meeting, MeetingRoom, MeetingParticipant, MeetingAttachment


@admin.register(MeetingRoom)
class MeetingRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'capacity', 'location', 'has_video_conf', 'has_projector', 'is_active')
    list_filter = ('is_active', 'has_video_conf', 'has_projector')
    search_fields = ('name', 'description', 'location')
    ordering = ('name',)


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'organizer', 'room', 'start_time', 'end_time', 'status', 'is_recurring')
    list_filter = ('status', 'is_recurring', 'recurrence_pattern', 'start_time')
    search_fields = ('title', 'description')
    raw_id_fields = ('organizer', 'room')
    date_hierarchy = 'start_time'
    ordering = ('-start_time',)


@admin.register(MeetingParticipant)
class MeetingParticipantAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'user', 'email', 'response', 'joined_at')
    list_filter = ('response', 'joined_at')
    raw_id_fields = ('meeting', 'user')
    search_fields = ('user__username', 'user__email', 'email')
    ordering = ('-meeting__start_time',)


@admin.register(MeetingAttachment)
class MeetingAttachmentAdmin(admin.ModelAdmin):
    list_display = ('meeting', 'file', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    raw_id_fields = ('meeting', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
