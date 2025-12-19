from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render

from accounts.forms import AdminUserCreateForm, CalDAVSettingsForm, MattermostSettingsForm, SidebarSettingsForm, UserProfileForm, UserRoleEditForm, UserThemeForm
from accounts.models import UserProfile
from organization.models import VacationPeriod, VacationRequest


@login_required
def profile(request):
    """
    Личный кабинет пользователя.
    Позволяет редактировать личные данные и заполнять график отпусков.
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    theme_form = UserThemeForm(request.POST or None, instance=profile)
    mattermost_form = MattermostSettingsForm(request.POST or None, instance=profile)
    sidebar_form = SidebarSettingsForm(request.POST or None, instance=profile)
    caldav_form = CalDAVSettingsForm(request.POST or None, instance=profile)

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "profile":
            form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect("profile")
        elif action == "theme":
            if theme_form.is_valid():
                theme_form.save()
                return redirect("profile")
        elif action == "mattermost":
            mattermost_form = MattermostSettingsForm(request.POST, instance=profile)
            if mattermost_form.is_valid():
                mattermost_form.save()
                return redirect("profile")
        elif action == "sidebar":
            if sidebar_form.is_valid():
                sidebar_form.save()
                return redirect("profile")
        elif action == "caldav":
            caldav_form = CalDAVSettingsForm(request.POST, instance=profile)
            if caldav_form.is_valid():
                caldav_form.save()
                return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)
        theme_form = UserThemeForm(instance=profile)
        mattermost_form = MattermostSettingsForm(instance=profile)
        sidebar_form = SidebarSettingsForm(instance=profile)
        caldav_form = CalDAVSettingsForm(instance=profile)

    # последние заявки по отпускам пользователя
    vacation_requests = request.user.vacation_requests.order_by("-created_at")[:5]

    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "theme_form": theme_form,
            "mattermost_form": mattermost_form,
            "sidebar_form": sidebar_form,
            "caldav_form": caldav_form,
            "vacation_requests": vacation_requests,
        },
    )


@login_required
def update_menu_settings(request):
    """
    API endpoint для обновления настроек меню.
    """
    import json
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        data = json.loads(request.body)
        
        # Обновление размера сайдбара
        if "sidebar_width" in data:
            profile.sidebar_width = int(data["sidebar_width"])
        if "sidebar_height" in data:
            profile.sidebar_height = data["sidebar_height"]
        if "sidebar_custom_enabled" in data:
            profile.sidebar_custom_enabled = data["sidebar_custom_enabled"] == True
        
        # Обновление настроек пунктов меню
        if "menu_items_settings" in data:
            profile.menu_items_settings = data["menu_items_settings"]
        
        # Обновление режима избранного
        if "menu_show_favorites_only" in data:
            profile.menu_show_favorites_only = data["menu_show_favorites_only"] == True
        
        profile.save()
        return JsonResponse({"success": True})
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
def toggle_menu_favorite(request):
    """
    API endpoint для переключения избранного для пункта меню.
    """
    import json
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        data = json.loads(request.body)
        menu_id = data.get("menu_id")
        
        if not menu_id:
            return JsonResponse({"error": "menu_id required"}, status=400)
        
        settings = profile.menu_items_settings or {}
        if menu_id not in settings:
            settings[menu_id] = {}
        
        current_favorite = settings[menu_id].get("favorite", False)
        settings[menu_id]["favorite"] = not current_favorite
        
        profile.menu_items_settings = settings
        profile.save()
        
        return JsonResponse({"success": True, "favorite": not current_favorite})
    
    return JsonResponse({"error": "Method not allowed"}, status=405)


def _is_portal_admin(user: User) -> bool:
    return user.is_authenticated and (user.is_staff or user.is_superuser)


@login_required
@user_passes_test(_is_portal_admin)
def user_roles(request):
    """
    Управление ролями пользователей (только для администраторов).
    """
    from accounts.forms import UserRoleEditForm

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "edit_role":
            # Обработка редактирования роли через чекбоксы
            user_id = request.POST.get("user_id")
            try:
                user = User.objects.get(pk=user_id)
                profile = user.profile
                profile.is_news_moderator = request.POST.get("is_news_moderator") == "on"
                profile.is_wiki_moderator = request.POST.get("is_wiki_moderator") == "on"
                profile.save()
                return redirect("user_roles")
            except User.DoesNotExist:
                pass
        else:
            # Обработка через форму (если используется)
            user_id = request.POST.get("user_id")
            try:
                user = User.objects.get(pk=user_id)
                profile = user.profile
                form = UserRoleEditForm(request.POST, instance=profile)
                if form.is_valid():
                    form.save()
                    return redirect("user_roles")
            except User.DoesNotExist:
                pass

    users = User.objects.all().order_by("username")
    return render(request, "accounts/user_roles.html", {"users": users})
