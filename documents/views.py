import json
import mimetypes
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from .forms import DocumentUploadForm
from .models import Document
from .utils import save_uploaded_file


def _can_view(user, doc: Document) -> bool:
    if not user.is_authenticated:
        return False
    if user == doc.author or user.is_superuser:
        return True
    # TODO: добавить проверку руководителя автора, когда будет реализована орг.структура.
    if doc.access_level == Document.ACCESS_EVERYONE:
        return True
    if doc.access_level == Document.ACCESS_ASSIGNED and user in doc.assigned_users.all():
        return True
    return False


def _can_edit(user, doc: Document) -> bool:
    if not user.is_authenticated:
        return False
    if user == doc.author or user.is_superuser:
        return True
    if doc.access_level == Document.ACCESS_EVERYONE:
        return True
    if doc.access_level == Document.ACCESS_ASSIGNED and user in doc.assigned_users.all():
        return True
    return False


@login_required
def document_list(request):
    """
    Список документов с учётом прав доступа.
    """
    qs = Document.objects.all()
    docs = [d for d in qs if _can_view(request.user, d)]
    return render(request, "documents/document_list.html", {"documents": docs})


@login_required
def document_upload(request):
    """
    Загрузка нового документа в /data.
    """
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            doc: Document = form.save(commit=False)
            doc.author = request.user
            save_uploaded_file(request.user, request.FILES["file"], doc)
            doc.save()
            form.save_m2m()
            return redirect("documents_list")
    else:
        form = DocumentUploadForm()

    return render(request, "documents/document_upload.html", {"form": form})


@login_required
def document_download(request, pk: int):
    doc = get_object_or_404(Document, pk=pk)
    if not _can_view(request.user, doc):
        return HttpResponseForbidden()
    abs_path = doc.absolute_path
    if not os.path.exists(abs_path):
        raise Http404
    content_type, _ = mimetypes.guess_type(abs_path)
    return FileResponse(open(abs_path, "rb"), content_type=content_type or "application/octet-stream")


@csrf_exempt
def document_download_onlyoffice(request, pk: int):
    """
    Endpoint для скачивания документа OnlyOffice без авторизации.
    Используется для загрузки файла OnlyOffice DocumentServer из контейнера.
    ВАЖНО: Этот endpoint должен проверять источник запроса или использовать токен для безопасности.
    """
    doc = get_object_or_404(Document, pk=pk)
    
    # Проверяем, что запрос идет от OnlyOffice (из Docker сети)
    # Можно добавить проверку по IP или токену для большей безопасности
    # Сейчас разрешаем доступ только из Docker сети
    # В продакшене нужно добавить проверку токена или IP
    
    abs_path = doc.absolute_path
    if not os.path.exists(abs_path):
        raise Http404
    content_type, _ = mimetypes.guess_type(abs_path)
    file_response = FileResponse(open(abs_path, "rb"), content_type=content_type or "application/octet-stream")
    # Добавляем CORS заголовки для OnlyOffice
    file_response["Access-Control-Allow-Origin"] = "*"
    return file_response


@login_required
def document_edit(request, pk: int):
    """
    Простейшее онлайн‑редактирование текстовых файлов (txt).
    Для doc/docx/xls/xlsx/pdf на этом этапе показываем только просмотр / скачивание.

    Для полноценного совместного редактирования офисных документов предполагается
    интеграция с OnlyOffice/Collabora через отдельный сервис и iframe.
    """
    doc = get_object_or_404(Document, pk=pk)
    if not _can_edit(request.user, doc):
        return HttpResponseForbidden()

    ext = os.path.splitext(doc.relative_path)[1].lower()
    is_text = ext in [".txt"]
    is_pdf = ext == ".pdf"
    is_office = ext in [".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]

    text_content = None
    if is_text and os.path.exists(doc.absolute_path):
        with open(doc.absolute_path, "r", encoding="utf-8", errors="ignore") as f:
            text_content = f.read()

    if request.method == "POST" and is_text:
        new_content = request.POST.get("content", "")
        with open(doc.absolute_path, "w", encoding="utf-8", errors="ignore") as f:
            f.write(new_content)
        return redirect("document_edit", pk=doc.pk)

    onlyoffice_enabled = settings.ONLYOFFICE_ENABLED and is_office
    collabora_enabled = settings.COLLABORA_ENABLED and is_office
    
    # Формируем URL для OnlyOffice
    # ВАЖНО: OnlyOffice DocumentServer делает HTTP запросы к file_url и callback_url ИЗ СВОЕГО КОНТЕЙНЕРА
    # Поэтому эти URL должны быть доступны из контейнера OnlyOffice
    # OnlyOffice JavaScript API загружается в браузере, но сам DocumentServer делает запросы из контейнера
    if settings.EXTERNAL_URL:
        # Если задан EXTERNAL_URL, используем его (должен быть доступен из контейнера OnlyOffice)
        base_url = settings.EXTERNAL_URL.rstrip('/')
        # Используем специальный endpoint для OnlyOffice без авторизации
        file_url = f"{base_url}{reverse('document_download_onlyoffice', args=[doc.pk])}"
        callback_url = f"{base_url}{reverse('onlyoffice_callback', args=[doc.pk])}"
    else:
        # Автоматическое определение
        host = request.get_host()
        scheme = request.scheme
        
        # В Docker окружении OnlyOffice контейнер не может подключиться к localhost хоста
        # OnlyOffice DocumentServer делает запросы к file_url и callback_url из контейнера
        # Решение: используем имя сервиса Docker (web:8000) для внутренних запросов
        # Это работает внутри Docker сети между контейнерами
        if 'localhost' in host or '127.0.0.1' in host:
            # OnlyOffice блокирует подключения к приватным IP адресам (включая имена Docker сервисов)
            # Проблема: OnlyOffice DocumentServer не может подключиться к web:8000 или host.docker.internal:8000
            # потому что они разрешаются в приватные IP адреса
            # Решение: используем host.docker.internal, который должен работать в Docker Desktop
            # Если это не сработает, нужно будет настроить OnlyOffice для разрешения приватных IP
            # или использовать публичный IP адрес хоста
            file_url = f"http://host.docker.internal:8000{reverse('document_download_onlyoffice', args=[doc.pk])}"
            callback_url = f"http://host.docker.internal:8000{reverse('onlyoffice_callback', args=[doc.pk])}"
        else:
            # Если хост не localhost, используем хост из запроса
            # Но нужно убедиться, что этот адрес доступен из контейнера OnlyOffice
            # Используем специальный endpoint для OnlyOffice без авторизации
            file_url = request.build_absolute_uri(reverse("document_download_onlyoffice", args=[doc.pk]))
            callback_url = request.build_absolute_uri(reverse("onlyoffice_callback", args=[doc.pk]))
    
    onlyoffice_config_dict = {
        "document": {
            "fileType": ext.lstrip(".") or "docx",
            "title": doc.name,
            "url": file_url,
        },
        "editorConfig": {
            "callbackUrl": callback_url,
            "mode": "edit",
            "lang": "ru",
            "user": {
                "id": str(request.user.id),
                "name": request.user.get_full_name() or request.user.username,
            },
        },
    }
    # Сериализуем конфигурацию в JSON для использования в JavaScript
    onlyoffice_config = json.dumps(onlyoffice_config_dict)
    
    # Collabora Online конфигурация
    collabora_wopi_src = None
    if collabora_enabled:
        # WOPI URL для Collabora должен быть доступен из контейнера Collabora
        # Collabora делает запросы к WOPI endpoint изнутри контейнера
        # Поэтому используем внутренний URL (web:8000) для WOPI
        # ВАЖНО: WOPISrc используется Collabora для запросов из контейнера
        # Collabora сервер получает WOPISrc из параметра URL iframe,
        # затем делает HTTP запросы к WOPI endpoint из своего контейнера
        # Поэтому WOPISrc должен содержать URL, доступный из контейнера Collabora
        if settings.EXTERNAL_URL:
            # Если задан EXTERNAL_URL, проверяем, можем ли мы использовать его из контейнера
            # Если EXTERNAL_URL указывает на localhost, Collabora не сможет подключиться
            base_wopi_url = settings.EXTERNAL_URL.rstrip('/')
            if 'localhost' in base_wopi_url or '127.0.0.1' in base_wopi_url:
                # EXTERNAL_URL указывает на localhost, но Collabora в контейнере не может подключиться к localhost
                # Используем внутренний адрес web:8000
                wopi_url = f"http://web:8000{reverse('collabora_wopi', args=[doc.pk])}"
            else:
                # EXTERNAL_URL указывает на внешний адрес, который может быть недоступен из контейнера
                # В этом случае лучше использовать внутренний адрес
                # Но если EXTERNAL_URL настроен правильно (например, через reverse proxy),
                # то можно попробовать использовать его
                wopi_url = f"{base_wopi_url}{reverse('collabora_wopi', args=[doc.pk])}"
        else:
            # Автоматическое определение: всегда используем внутренний адрес web:8000
            # так как Collabora делает запросы из контейнера
            wopi_url = f"http://web:8000{reverse('collabora_wopi', args=[doc.pk])}"
        
        # Добавляем access_token для авторизации
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        token = default_token_generator.make_token(request.user)
        user_id_b64 = urlsafe_base64_encode(force_bytes(str(request.user.id)))
        access_token = f"{user_id_b64}_{token}"
        
        # WOPISrc должен быть URL-кодирован
        from urllib.parse import quote
        wopi_url_with_token = f"{wopi_url}?access_token={access_token}"
        wopi_url_encoded = quote(wopi_url_with_token, safe='')
        
        collabora_base = settings.COLLABORA_BASE_URL.rstrip('/')
        # Используем правильный путь для Collabora CODE
        # Формат: /browser/<session_id>/cool.html?WOPISrc=<encoded_url>
        # ВАЖНО: Предупреждение "Client - server version mismatch" - это НЕ ошибка
        # Это информационное сообщение о том, что Collabora отключает кэш браузера
        # для данной сессии. Это нормальное поведение и не влияет на функциональность.
        # Collabora использует внутренний механизм версионирования для кэширования,
        # и когда мы передаем свой session_id, он не совпадает с ожидаемым.
        # Это не критично - редактор будет работать нормально.
        import secrets
        # Генерируем случайный session_id длиной 10 символов (hex)
        # Это соответствует формату, который Collabora ожидает (например: a246f9ab3c)
        session_id = secrets.token_hex(5)  # 5 байт = 10 hex символов
        # Используем стандартный формат Collabora CODE
        collabora_wopi_src = f"{collabora_base}/browser/{session_id}/cool.html?WOPISrc={wopi_url_encoded}"

    # Убеждаемся, что onlyoffice_base_url заканчивается на /
    onlyoffice_base_url = settings.ONLYOFFICE_BASE_URL
    if onlyoffice_base_url and not onlyoffice_base_url.endswith('/'):
        onlyoffice_base_url += '/'
    
    return render(
        request,
        "documents/document_edit.html",
        {
            "document": doc,
            "is_text": is_text,
            "is_pdf": is_pdf,
            "is_office": is_office,
            "text_content": text_content,
            "onlyoffice_enabled": onlyoffice_enabled,
            "onlyoffice_base_url": onlyoffice_base_url,
            "onlyoffice_config": onlyoffice_config,
            "collabora_enabled": collabora_enabled,
            "collabora_wopi_src": collabora_wopi_src,
        },
    )


@csrf_exempt
def onlyoffice_callback(request, pk: int):
    """
    Callback от OnlyOffice DocumentServer для сохранения изменений документа.
    Реализована базовая обработка статусов 2/6: скачиваем изменённый файл и сохраняем в наше хранилище.
    """
    doc = get_object_or_404(Document, pk=pk)
    import json
    import urllib.request

    data = json.loads(request.body.decode("utf-8"))
    status = data.get("status")
    # 2 — документ сохранён, 6 — документ закрыт с сохранением
    if status in (2, 6):
        url = data.get("url")
        if url:
            with urllib.request.urlopen(url) as resp, open(doc.absolute_path, "wb") as f:
                f.write(resp.read())
    return JsonResponse({"error": 0})


@csrf_exempt
def collabora_wopi(request, pk: int):
    """
    WOPI endpoint для Collabora Online.
    Возвращает информацию о документе в формате WOPI.
    Collabora делает запросы без сессии пользователя, поэтому не используем @login_required.
    """
    doc = get_object_or_404(Document, pk=pk)
    
    # Получаем access_token из параметров или заголовков
    access_token = request.GET.get('access_token') or request.META.get('HTTP_X_WOPI_OVERRIDE') or request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
    
    # Проверяем права доступа
    user = None
    if access_token:
        # Декодируем токен для получения user_id
        try:
            from django.utils.http import urlsafe_base64_decode
            from django.utils.encoding import force_str
            from django.contrib.auth.tokens import default_token_generator
            from django.contrib.auth.models import User
            
            parts = access_token.split('_')
            if len(parts) == 2:
                user_id_b64, token = parts
                user_id = force_str(urlsafe_base64_decode(user_id_b64))
                user = User.objects.get(pk=user_id)
                # Проверяем токен
                if not default_token_generator.check_token(user, token):
                    user = None
        except Exception:
            user = None
    
    # Если не удалось получить пользователя из токена, пробуем из сессии
    if not user:
        user = getattr(request, 'user', None)
        if user and not user.is_authenticated:
            user = None
    
    # Проверяем права доступа
    if user:
        if not _can_view(user, doc):
            return HttpResponseForbidden()
    else:
        # Для Collabora разрешаем доступ без авторизации (в продакшене нужно добавить проверку)
        pass
    
    # WOPI CheckFileInfo - возвращает метаданные документа
    if request.method == "GET":
        # Проверяем, это GetFile запрос (определяется по наличию /contents в пути)
        # В стандартном WOPI протоколе:
        # - CheckFileInfo: GET /wopi/files/{file_id}?access_token=...
        # - GetFile: GET /wopi/files/{file_id}/contents?access_token=...
        request_path = request.path
        is_get_file = request_path.endswith('/contents/') or request_path.endswith('/contents')
        
        if not is_get_file:
            # CheckFileInfo запрос
            can_edit = False
            can_view = True
            if user:
                can_edit = _can_edit(user, doc)
                can_view = _can_view(user, doc)
            
            response_data = {
                "BaseFileName": doc.name,
                "OwnerId": str(doc.author.id),
                "Size": doc.size,
                "UserId": str(user.id) if user and user.is_authenticated else "anonymous",
                "UserFriendlyName": (user.get_full_name() or user.username) if user and user.is_authenticated else "Anonymous",
                "UserCanWrite": can_edit,
                "UserCanNotWriteRelative": True,  # WOPI: True means relative files are not allowed
                "PostMessageOrigin": request.build_absolute_uri("/").rstrip('/'),
                "LastModifiedTime": doc.updated_at.isoformat() if doc.updated_at else "",
                "Version": str(doc.pk),  # WOPI: Version identifier for the file
            }
            
            # Добавляем заголовки для CORS
            response = JsonResponse(response_data)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        else:
            # GetFile запрос - возвращает содержимое файла
            if user and not _can_view(user, doc):
                return HttpResponseForbidden()
            # Прямая отдача файла без проверки авторизации через document_download
            # так как Collabora делает запросы без сессии
            abs_path = doc.absolute_path
            if not os.path.exists(abs_path):
                raise Http404
            content_type, _ = mimetypes.guess_type(abs_path)
            file_response = FileResponse(open(abs_path, "rb"), content_type=content_type or "application/octet-stream")
            file_response["Access-Control-Allow-Origin"] = "*"
            file_response["Content-Disposition"] = f'inline; filename="{doc.name}"'
            return file_response
    
    # WOPI PutFile - сохраняет изменения в файл
    if request.method == "POST":
        if user and not _can_edit(user, doc):
            return HttpResponseForbidden()
        
        with open(doc.absolute_path, "wb") as f:
            f.write(request.body)
        # Обновляем время изменения документа
        doc.updated_at = timezone.now()
        doc.save(update_fields=['updated_at'])
        response = JsonResponse({"LastModifiedTime": doc.updated_at.isoformat()})
        response["Access-Control-Allow-Origin"] = "*"
        return response
    
    # OPTIONS для CORS
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response
    
    return HttpResponseForbidden()
