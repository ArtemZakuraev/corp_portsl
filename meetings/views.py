"""Meetings app views with optimized queries."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from datetime import timedelta

from .models import Meeting, MeetingRoom, MeetingParticipant, MeetingStatus


@login_required
def meeting_list(request):
    """List all meetings with filtering."""
    queryset = Meeting.objects.select_related(
        'organizer', 'room'
    ).prefetch_related('participants__user')

    # Filter by status
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    # Filter by date range
    date_filter = request.GET.get('date')
    now = timezone.now()
    if date_filter == 'today':
        queryset = queryset.filter(
            start_time__date=now.date()
        )
    elif date_filter == 'week':
        queryset = queryset.filter(
            start_time__gte=now.date(),
            start_time__lt=now.date() + timedelta(days=7)
        )
    elif date_filter == 'month':
        queryset = queryset.filter(
            start_time__gte=now.date(),
            start_time__lt=now.replace(day=28) + timedelta(days=4)
        )
    elif date_filter == 'past':
        queryset = queryset.filter(end_time__lt=now)
    else:
        # Default: upcoming meetings
        queryset = queryset.filter(start_time__gte=now)

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(organizer__last_name__icontains=search_query)
        )

    paginator = Paginator(queryset, 15)
    page = request.GET.get('page')
    meetings = paginator.get_page(page)

    rooms = MeetingRoom.objects.filter(is_active=True)

    context = {
        'meetings': meetings,
        'rooms': rooms,
        'statuses': MeetingStatus.choices,
        'selected_status': status,
        'date_filter': date_filter,
        'search_query': search_query,
    }
    return render(request, 'meetings/meeting_list.html', context)


@login_required
def meeting_detail(request, pk):
    """Meeting detail view."""
    meeting = get_object_or_404(
        Meeting.objects.select_related(
            'organizer', 'room'
        ).prefetch_related(
            'participants__user',
            'attachments'
        ),
        pk=pk
    )

    # Check if current user is participant
    is_participant = False
    user_response = None
    if request.user.is_authenticated:
        try:
            participant = MeetingParticipant.objects.get(
                meeting=meeting,
                user=request.user
            )
            is_participant = True
            user_response = participant.response
        except MeetingParticipant.DoesNotExist:
            pass

    context = {
        'meeting': meeting,
        'is_participant': is_participant,
        'user_response': user_response,
        'statuses': MeetingStatus.choices,
    }
    return render(request, 'meetings/meeting_detail.html', context)


@login_required
def create_meeting(request):
    """Create new meeting."""
    if request.method == 'POST':
        meeting = Meeting.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            organizer=request.user,
            room_id=request.POST.get('room'),
            start_time=request.POST.get('start_time'),
            end_time=request.POST.get('end_time'),
            status=MeetingStatus.SCHEDULED,
            is_recurring=request.POST.get('is_recurring') == 'on',
            recurrence_pattern=request.POST.get('recurrence_pattern', ''),
            meeting_link=request.POST.get('meeting_link', ''),
        )
        
        # Add participants
        participant_ids = request.POST.getlist('participants')
        for user_id in participant_ids:
            MeetingParticipant.objects.create(
                meeting=meeting,
                user_id=user_id,
                response='pending'
            )
        
        return redirect('meetings:detail', pk=meeting.pk)
    
    rooms = MeetingRoom.objects.filter(is_active=True)
    return render(request, 'meetings/meeting_form.html', {
        'rooms': rooms,
        'meeting': None,
        'statuses': MeetingStatus.choices,
    })


@login_required
def edit_meeting(request, pk):
    """Edit existing meeting."""
    meeting = get_object_or_404(Meeting, pk=pk)
    
    if request.method == 'POST':
        meeting.title = request.POST.get('title')
        meeting.description = request.POST.get('description')
        meeting.room_id = request.POST.get('room')
        meeting.start_time = request.POST.get('start_time')
        meeting.end_time = request.POST.get('end_time')
        meeting.status = request.POST.get('status', MeetingStatus.SCHEDULED)
        meeting.is_recurring = request.POST.get('is_recurring') == 'on'
        meeting.recurrence_pattern = request.POST.get('recurrence_pattern', '')
        meeting.meeting_link = request.POST.get('meeting_link', '')
        meeting.save()
        return redirect('meetings:detail', pk=meeting.pk)
    
    rooms = MeetingRoom.objects.filter(is_active=True)
    return render(request, 'meetings/meeting_form.html', {
        'meeting': meeting,
        'rooms': rooms,
        'statuses': MeetingStatus.choices,
    })


@login_required
@require_http_methods(["POST"])
def rsvp(request, pk):
    """RSVP to meeting invitation."""
    meeting = get_object_or_404(Meeting, pk=pk)
    response = request.POST.get('response', 'pending')
    
    participant, created = MeetingParticipant.objects.get_or_create(
        meeting=meeting,
        user=request.user,
        defaults={'response': response}
    )
    
    if not created:
        participant.response = response
        if response == 'accepted':
            participant.joined_at = timezone.now()
        participant.save()
    
    return JsonResponse({'success': True, 'response': participant.get_response_display()})


@login_required
@require_http_methods(["POST"])
def update_status(request, pk):
    """Update meeting status."""
    meeting = get_object_or_404(Meeting, pk=pk)
    status = request.POST.get('status')
    
    if status in dict(MeetingStatus.choices):
        meeting.status = status
        meeting.save(update_fields=['status'])
        return JsonResponse({'success': True, 'status': meeting.get_status_display()})
    
    return JsonResponse({'success': False}, status=400)
