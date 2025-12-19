from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import models
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import SelfTaskForm, TaskForm, SubordinateTaskForm
from .models import Task
from .utils import get_user_subordinates


@login_required
def create_task(request):
    """
    Создание задачи пользователем.
    После сохранения отправляется письмо исполнителю со ссылкой на задачу.
    """
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task: Task = form.save(commit=False)
            task.created_by = request.user
            # опционально можно связать с исполнителем, если email совпадает
            task.save()

            link = request.build_absolute_uri(
                reverse("task_external_view", kwargs={"token": str(task.token)})
            )
            subject = f"Новая задача: {task.title}"
            message = (
                f"Вам назначена задача:\n\n"
                f"{task.title}\n\n"
                f"{task.description}\n\n"
                f"Перейдите по ссылке для просмотра и выполнения задачи:\n{link}\n"
            )
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [task.assignee_email],
                fail_silently=True,
            )

            return redirect("tasks")
    else:
        form = TaskForm()

    tasks = Task.objects.filter(created_by=request.user).order_by("-created_at")

    return render(
        request,
        "tasks/create_task.html",
        {
            "form": form,
            "tasks": tasks,
        },
    )


@login_required
def my_tasks(request):
    """
    Раздел «Мои задачи» — задачи, которые пользователь ставит самому себе,
    а также задачи, которые назначены пользователю другими руководителями.
    Поддерживает канбан-доску и список, сортировку по важности и дате.
    """
    from accounts.models import UserProfile
    
    # Получаем или создаем профиль пользователя
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    # Проверяем, есть ли у пользователя подчиненные
    from organization.models import Department, Unit
    subordinates = get_user_subordinates(request.user)
    user_has_subordinates = subordinates.exists()
    
    # Для отладки: проверяем, является ли пользователь руководителем
    debug_info = {
        'is_dept_head': Department.objects.filter(
            models.Q(head=request.user) | models.Q(department_head__user=request.user)
        ).exists(),
        'is_unit_head': Unit.objects.filter(
            models.Q(head=request.user) | models.Q(unit_head__user=request.user)
        ).exists(),
        'subordinates_count': subordinates.count(),
    }
    
    # Обработка изменения настроек отображения
    if request.method == "POST":
        action = request.POST.get("action")
        
        if action == "change_view_mode":
            view_mode = request.POST.get("view_mode")
            if view_mode in ["list", "kanban"]:
                profile.task_view_mode = view_mode
                profile.save()
                return redirect("tasks")
        elif action == "change_sort_by":
            sort_by = request.POST.get("sort_by")
            if sort_by in ["priority", "due_date", "created_at"]:
                profile.task_sort_by = sort_by
                profile.save()
                return redirect("tasks")
        elif action == "update_priority_colors":
            profile.task_priority_important_color = request.POST.get("important_color", "#4CAF50")
            profile.task_priority_urgent_color = request.POST.get("urgent_color", "#FF9800")
            profile.task_priority_critical_color = request.POST.get("critical_color", "#F44336")
            profile.save()
            return redirect("tasks")
        elif action == "create_subordinate_task":
            # Создание задачи для подчиненного
            form = SubordinateTaskForm(request.POST, user=request.user)
            if form.is_valid():
                task: Task = form.save(commit=False)
                task.created_by = request.user
                task.assignee_email = task.assignee.email or ""
                task.save()
                # Отправляем уведомление подчиненному
                link = request.build_absolute_uri(
                    reverse("tasks")
                )
                subject = f"Новая задача от руководителя: {task.title}"
                message = (
                    f"Вам назначена задача:\n\n"
                    f"{task.title}\n\n"
                    f"{task.description}\n\n"
                    f"Постановщик: {request.user.get_full_name() or request.user.username}\n\n"
                    f"Перейдите по ссылке для просмотра и выполнения задачи:\n{link}\n"
                )
                if task.assignee.email:
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [task.assignee.email],
                        fail_silently=True,
                    )
                return redirect("tasks")
        else:
            # Обычное создание задачи
            form = SelfTaskForm(request.POST)
            if form.is_valid():
                task: Task = form.save(commit=False)
                task.created_by = request.user
                task.assignee = request.user
                task.assignee_email = request.user.email or ""
                task.save()
                return redirect("tasks")
    else:
        form = SelfTaskForm()

    # Получаем задачи пользователя:
    # 1. Задачи, которые пользователь создал сам себе
    # 2. Задачи, которые назначены пользователю другими руководителями
    tasks = Task.objects.filter(
        models.Q(created_by=request.user) | models.Q(assignee=request.user)
    )
    
    # Применяем сортировку
    sort_by = profile.task_sort_by or "due_date"
    if sort_by == "priority":
        # Сортируем по важности: критично > срочно > важно > без важности
        # Используем аннотацию для сортировки
        from django.db.models import Case, When, IntegerField
        tasks = tasks.annotate(
            priority_order=Case(
                When(priority="critical", then=0),
                When(priority="urgent", then=1),
                When(priority="important", then=2),
                default=3,
                output_field=IntegerField(),
            )
        ).order_by("priority_order", "due_date", "-created_at")
    elif sort_by == "due_date":
        tasks = tasks.order_by("due_date", "status", "-created_at")
    elif sort_by == "created_at":
        tasks = tasks.order_by("-created_at", "status", "due_date")
    else:
        tasks = tasks.order_by("due_date", "status", "-created_at")
    
    # Преобразуем QuerySet в список для группировки
    tasks_list = list(tasks)
    
    # Группируем задачи по статусам для канбан-доски
    tasks_by_status = {
        "new": [],
        "in_progress": [],
        "done": [],
    }
    for task in tasks_list:
        tasks_by_status[task.status].append(task)

    # Форма для создания задачи подчиненному (если есть подчиненные)
    subordinate_form = None
    if user_has_subordinates:
        subordinate_form = SubordinateTaskForm(user=request.user)
    
    return render(
        request,
        "tasks/my_tasks.html",
        {
            "form": form,
            "subordinate_form": subordinate_form,
            "user_has_subordinates": user_has_subordinates,
            "subordinates": subordinates,
            "debug_info": debug_info,
            "tasks": tasks_list,
            "tasks_by_status": tasks_by_status,
            "view_mode": profile.task_view_mode or "list",
            "sort_by": profile.task_sort_by or "due_date",
            "priority_colors": {
                "important": profile.task_priority_important_color or "#4CAF50",
                "urgent": profile.task_priority_urgent_color or "#FF9800",
                "critical": profile.task_priority_critical_color or "#F44336",
            },
        },
    )


def task_external_view(request, token: str):
    """
    Просмотр задачи по токену без необходимости авторизации.
    """
    try:
        task = get_object_or_404(Task, token=token)
    except (ValueError, Task.DoesNotExist) as exc:  # type: ignore[misc]
        raise Http404 from exc

    return render(request, "tasks/task_external.html", {"task": task})


@login_required
@require_http_methods(["POST"])
def update_task_status(request, task_id):
    """
    API endpoint для обновления статуса задачи через drag-and-drop.
    """
    try:
        task = Task.objects.get(pk=task_id, created_by=request.user)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Задача не найдена"}, status=404)
    
    new_status = request.POST.get("status")
    if new_status not in dict(Task.STATUS_CHOICES).keys():
        return JsonResponse({"error": "Неверный статус"}, status=400)
    
    task.status = new_status
    task.save()
    
    # Подсчитываем количество невыполненных задач для обновления счетчика в меню
    tasks_count = Task.objects.filter(
        models.Q(created_by=request.user) | models.Q(assignee=request.user)
    ).exclude(status="done").count()
    
    return JsonResponse({
        "success": True, 
        "status": new_status, 
        "status_display": task.get_status_display(),
        "tasks_count": tasks_count,
        "in_progress_count": tasks_count
    })


@login_required
@require_http_methods(["GET"])
def get_tasks_count(request):
    """
    API endpoint для получения количества невыполненных задач.
    Учитываются задачи, которые пользователь создал сам себе, и задачи, назначенные ему руководителями.
    """
    tasks_count = Task.objects.filter(
        models.Q(created_by=request.user) | models.Q(assignee=request.user)
    ).exclude(status="done").count()
    return JsonResponse({"tasks_count": tasks_count, "in_progress_count": tasks_count})
