import os
import uuid
from typing import Tuple

from django.conf import settings
from django.contrib.auth import get_user_model

from .models import Document

User = get_user_model()


STORAGE_LOCAL = "local"
STORAGE_S3 = "s3"


def get_storage_type() -> str:
    """
    Возвращает активный тип хранилища документов.
    Берётся из Django settings.DOCUMENT_STORAGE_TYPE, по умолчанию — локальный диск.
    """
    return getattr(settings, "DOCUMENT_STORAGE_TYPE", STORAGE_LOCAL)


def _ensure_data_dir() -> None:
    os.makedirs(settings.DATA_ROOT, exist_ok=True)


def _save_file_local(uploaded_file) -> Tuple[str, int]:
    """
    Сохраняет файл в локальное хранилище /data с уникальным именем.
    Возвращает (relative_path, size).
    """
    _ensure_data_dir()
    ext = os.path.splitext(uploaded_file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    abs_path = settings.DATA_ROOT / unique_name

    with abs_path.open("wb") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)

    size = abs_path.stat().st_size
    return unique_name, size


def save_uploaded_file(user: User, uploaded_file, document: Document) -> None:
    """
    Сохраняет загруженный файл в выбранное хранилище и обновляет поля документа.
    Сейчас реализован локальный диск, для S3 предусмотрен интерфейс и настройки.
    """
    storage_type = get_storage_type()

    if storage_type == STORAGE_LOCAL:
        relative_path, size = _save_file_local(uploaded_file)
        document.relative_path = relative_path
        document.size = size
    elif storage_type == STORAGE_S3:
        # Заглушка для S3-совместимого хранилища.
        # Здесь можно реализовать загрузку через boto3, minio и т.п.
        # Пока сохраняем в локальное хранилище как fallback, но с префиксом.
        relative_path, size = _save_file_local(uploaded_file)
        document.relative_path = f"s3_fallback/{relative_path}"
        document.size = size
    else:
        # Некорректная конфигурация — используем локальное хранилище по умолчанию.
        relative_path, size = _save_file_local(uploaded_file)
        document.relative_path = relative_path
        document.size = size




