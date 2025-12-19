from django.contrib import admin

from .models import DepartmentHead, MattermostSettings, Position, PortalSettings, UnitHead


@admin.register(PortalSettings)
class PortalSettingsAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для настройки оформления портала.
    Рекомендуется хранить только одну запись (id=1).
    """

    list_display = ("site_name",)


@admin.register(DepartmentHead)
class DepartmentHeadAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для управления руководителями департаментов.
    """

    list_display = ("last_name", "first_name", "middle_name", "department_name", "user")
    list_filter = ("department_name",)
    search_fields = ("last_name", "first_name", "middle_name", "department_name", "user__username", "user__email")


@admin.register(UnitHead)
class UnitHeadAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для управления руководителями отделов.
    """

    list_display = ("last_name", "first_name", "middle_name", "unit_name", "user")
    list_filter = ("unit_name",)
    search_fields = ("last_name", "first_name", "middle_name", "unit_name", "user__username", "user__email")


@admin.register(MattermostSettings)
class MattermostSettingsAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для настройки сервера Mattermost.
    Рекомендуется хранить только одну запись (id=1).
    """

    list_display = ("server_url", "api_version")


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    """
    Админ-интерфейс для управления справочником должностей.
    """

    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)

