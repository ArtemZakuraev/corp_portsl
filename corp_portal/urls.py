"""
URL configuration for corp_portal project.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from organization import views as org_views
from news.views import news_list, news_create
from tasks.views import create_task, task_external_view, update_task_status, get_tasks_count
from accounts.views import profile, user_roles, update_menu_settings, toggle_menu_favorite
from documents import views as document_views
from documents.views import (
    document_download,
    document_download_onlyoffice,
    document_edit,
    document_list,
    document_upload,
    onlyoffice_callback,
)
from wiki import views as wiki_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", org_views.home, name="home"),

    # Стандартные auth-URL (login, logout и т.п.)
    path("accounts/", include("django.contrib.auth.urls")),

    # Рабочий стол
    path("tasks/", org_views.tasks, name="tasks"),
    path("account/profile/", profile, name="profile"),
    path("tasks/create/", create_task, name="task_create"),
    path("tasks/external/<uuid:token>/", task_external_view, name="task_external_view"),
    path("tasks/<int:task_id>/update-status/", update_task_status, name="update_task_status"),
    path("api/tasks/count/", get_tasks_count, name="get_tasks_count"),
    path("api/menu/settings/", update_menu_settings, name="update_menu_settings"),
    path("api/menu/favorite/", toggle_menu_favorite, name="toggle_menu_favorite"),
    path("meetings/", org_views.meetings, name="meetings"),

    # Организация
    path("employees/", org_views.employees, name="employees"),
    path("org-chart/", org_views.org_chart, name="org_chart"),
    path("units/", org_views.units, name="units"),
    path("units/<int:pk>/edit/", org_views.unit_edit, name="unit_edit"),
    path("departments/<int:pk>/edit/", org_views.department_edit, name="department_edit"),

    # Коммуникации
    path("news/", news_list, name="news_list"),
    path("news/create/", news_create, name="news_create"),
    path("chats/", org_views.chats, name="chats"),
    path("mattermost-files/<str:file_subdir>/<str:file_name>", org_views.mattermost_file_view, name="mattermost_file"),
    
    # База знаний
    path("wiki/", wiki_views.wiki_list, name="wiki_list"),
    path("wiki/create/", wiki_views.wiki_create, name="wiki_create"),
    # Группы просмотра (должны быть выше общего маршрута wiki/<str:slug>/)
    path("wiki/groups/", wiki_views.wiki_groups_list, name="wiki_groups_list"),
    path("wiki/groups/create/", wiki_views.wiki_group_create, name="wiki_group_create"),
    path("wiki/groups/<int:group_id>/edit/", wiki_views.wiki_group_edit, name="wiki_group_edit"),
    path("wiki/groups/<int:group_id>/delete/", wiki_views.wiki_group_delete, name="wiki_group_delete"),
    # Загрузка изображений для редактора
    path("wiki/upload-image/", wiki_views.wiki_upload_image, name="wiki_upload_image"),
    # Остальные маршруты wiki (должны быть после групп)
    path("wiki/image/<int:image_id>/delete/", wiki_views.wiki_delete_image, name="wiki_delete_image"),
    path("wiki/file/<int:file_id>/delete/", wiki_views.wiki_delete_file, name="wiki_delete_file"),
    path("wiki/file/<int:file_id>/download/", wiki_views.wiki_file_download, name="wiki_file_download"),
    path("wiki/<str:slug>/edit/", wiki_views.wiki_edit, name="wiki_edit"),
    path("wiki/<str:slug>/", wiki_views.wiki_article, name="wiki_article"),
    
    # О системе
    path("about/", org_views.about, name="about"),
    
    # API для настройки ленты
    path("api/dashboard/order/", org_views.save_dashboard_order, name="save_dashboard_order"),
    
    # Отпуска
    path("vacations/", org_views.vacations, name="vacations"),

    # Документы и процессы
    path("documents/", document_list, name="documents_list"),
    path("documents/upload/", document_upload, name="documents_upload"),
    path("documents/<int:pk>/download/", document_download, name="document_download"),
    path("documents/<int:pk>/onlyoffice/download/", document_download_onlyoffice, name="document_download_onlyoffice"),
    path("documents/<int:pk>/", document_edit, name="document_edit"),
    path("documents/<int:pk>/onlyoffice/callback/", onlyoffice_callback, name="onlyoffice_callback"),
    path("documents/<int:pk>/collabora/wopi/", document_views.collabora_wopi, name="collabora_wopi"),
    path("documents/<int:pk>/collabora/wopi/contents/", document_views.collabora_wopi, name="collabora_wopi_contents"),
    path("processes/", org_views.processes, name="processes"),
    path("hr-services/", org_views.hr_services, name="hr_services"),

    # Администрирование
    path("portal-settings/", org_views.portal_settings_page, name="portal_settings_page"),
    path("user-roles/", user_roles, name="user_roles"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
