"""Tasks app views with optimized queries."""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count, Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from .models import Task, TaskStatus, Priority, TaskComment, TaskAttachment


@login_required
def task_list(request):
    """List all tasks with filtering and pagination."""
    queryset = Task.objects.select_related(
        'author', 'assignee', 'parent_task'
    ).prefetch_related('subtasks')

    # Filter by status
    status = request.GET.get('status')
    if status:
        queryset = queryset.filter(status=status)

    # Filter by priority
    priority = request.GET.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)

    # Filter by assignee
    assignee_id = request.GET.get('assignee')
    if assignee_id:
        queryset = queryset.filter(assignee_id=assignee_id)
    else:
        # Show only tasks assigned to current user or created by user
        queryset = queryset.filter(
            Q(assignee=request.user) | Q(author=request.user)
        )

    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )

    # Sort
    sort_by = request.GET.get('sort', '-created_at')
    if sort_by in ['due_date', 'priority', 'status', 'created_at']:
        queryset = queryset.order_by(sort_by)
    elif sort_by == '-due_date':
        queryset = queryset.order_by('-due_date')
    else:
        queryset = queryset.order_by('-created_at')

    paginator = Paginator(queryset, 20)
    page = request.GET.get('page')
    tasks = paginator.get_page(page)

    context = {
        'tasks': tasks,
        'statuses': TaskStatus.choices,
        'priorities': Priority.choices,
        'selected_status': status,
        'selected_priority': priority,
        'search_query': search_query,
        'sort_by': sort_by,
    }
    return render(request, 'tasks/task_list.html', context)


@login_required
def task_detail(request, pk):
    """Task detail view."""
    task = get_object_or_404(
        Task.objects.select_related(
            'author', 'assignee', 'parent_task'
        ).prefetch_related(
            'subtasks',
            'comments__author',
            'attachments'
        ),
        pk=pk
    )

    # Add comment
    if request.method == 'POST' and request.POST.get('comment'):
        TaskComment.objects.create(
            task=task,
            author=request.user,
            content=request.POST.get('comment')
        )
        return redirect('tasks:detail', pk=pk)

    context = {
        'task': task,
        'statuses': TaskStatus.choices,
        'priorities': Priority.choices,
    }
    return render(request, 'tasks/task_detail.html', context)


@login_required
@require_http_methods(["POST"])
def update_status(request, pk):
    """Update task status via AJAX."""
    task = get_object_or_404(Task, pk=pk)
    
    status = request.POST.get('status')
    if status in dict(TaskStatus.choices):
        task.status = status
        if status == TaskStatus.DONE:
            task.completed_at = timezone.now()
            task.progress = 100
        task.save(update_fields=['status', 'completed_at', 'progress'])
        return JsonResponse({'success': True, 'status': task.get_status_display()})
    
    return JsonResponse({'success': False}, status=400)


@login_required
def create_task(request):
    """Create new task."""
    if request.method == 'POST':
        task = Task.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            author=request.user,
            assignee_id=request.POST.get('assignee'),
            priority=request.POST.get('priority', Priority.MEDIUM),
            due_date=request.POST.get('due_date') or None,
            parent_task_id=request.POST.get('parent_task') or None,
        )
        return redirect('tasks:detail', pk=task.pk)
    
    return render(request, 'tasks/task_form.html', {
        'priorities': Priority.choices,
        'task': None,
    })


@login_required
def edit_task(request, pk):
    """Edit existing task."""
    task = get_object_or_404(Task, pk=pk)
    
    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.assignee_id = request.POST.get('assignee')
        task.priority = request.POST.get('priority', Priority.MEDIUM)
        task.due_date = request.POST.get('due_date') or None
        task.parent_task_id = request.POST.get('parent_task') or None
        task.save()
        return redirect('tasks:detail', pk=task.pk)
    
    return render(request, 'tasks/task_form.html', {
        'task': task,
        'priorities': Priority.choices,
    })
