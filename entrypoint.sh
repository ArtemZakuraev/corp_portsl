#!/bin/bash
set -e

# Функция для ожидания готовности базы данных
wait_for_db() {
    echo "Ожидание готовности базы данных..."
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if python -c "
import sys
import psycopg2
import os
try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        user=os.getenv('POSTGRES_USER', 'corp_portal'),
        password=os.getenv('POSTGRES_PASSWORD', 'corp_portal'),
        dbname=os.getenv('POSTGRES_DB', 'corp_portal'),
        connect_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
            echo "База данных готова!"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Попытка $attempt/$max_attempts: База данных еще не готова, ожидание..."
        sleep 2
    done
    
    echo "Ошибка: Не удалось подключиться к базе данных после $max_attempts попыток"
    exit 1
}

# Функция для установки SSL сертификатов OnlyOffice
install_onlyoffice_cert() {
    echo "=========================================="
    echo "Установка SSL сертификата OnlyOffice..."
    echo "=========================================="
    
    CERT_FILE="/certs/onlyoffice.crt"
    
    if [ -f "$CERT_FILE" ]; then
        echo "Найден сертификат OnlyOffice: $CERT_FILE"
        
        # Копируем сертификат в хранилище доверенных сертификатов
        CERT_NAME="onlyoffice.crt"
        cp "$CERT_FILE" "/usr/local/share/ca-certificates/$CERT_NAME"
        
        # Обновляем хранилище сертификатов
        if update-ca-certificates 2>/dev/null; then
            echo "✓ Сертификат OnlyOffice успешно установлен в доверенные!"
        else
            echo "⚠ Предупреждение: Не удалось обновить хранилище сертификатов"
        fi
    else
        echo "⚠ Предупреждение: Сертификат OnlyOffice не найден: $CERT_FILE"
        echo "  Убедитесь, что сертификат сгенерирован: docker-compose --profile cert run --rm cert_generator"
    fi
}

# Устанавливаем SSL сертификат OnlyOffice
install_onlyoffice_cert

# Ожидаем готовности базы данных
wait_for_db

# Применяем миграции для всех приложений
echo "=========================================="
echo "Применение миграций базы данных..."
echo "=========================================="

# Применяем миграции с несколькими попытками
max_migrate_attempts=3
migrate_attempt=0
migration_success=false

while [ $migrate_attempt -lt $max_migrate_attempts ]; do
    migrate_attempt=$((migrate_attempt + 1))
    echo "Попытка применения миграций: $migrate_attempt/$max_migrate_attempts"
    
    if python manage.py migrate --noinput --verbosity=1; then
        echo "✓ Миграции успешно применены!"
        migration_success=true
        break
    else
        echo "⚠ Попытка $migrate_attempt не удалась, повторная попытка через 2 секунды..."
        sleep 2
    fi
done

if [ "$migration_success" = false ]; then
    echo "✗ ОШИБКА: Не удалось применить миграции после $max_migrate_attempts попыток!"
    echo "Проверьте логи выше для деталей."
    exit 1
fi

# Проверяем, что нет непримененных миграций
echo "Проверка наличия непримененных миграций..."
unapplied=$(python manage.py showmigrations --list 2>/dev/null | grep -c "\[ \]" || echo "0")

if [ "$unapplied" -gt 0 ]; then
    echo "⚠ ВНИМАНИЕ: Обнаружены $unapplied непримененных миграций!"
    echo "Список непримененных миграций:"
    python manage.py showmigrations --list | grep "\[ \]"
    echo "Попытка применить оставшиеся миграции..."
    python manage.py migrate --noinput --verbosity=1
    if [ $? -eq 0 ]; then
        echo "✓ Все оставшиеся миграции применены!"
    else
        echo "⚠ Не удалось применить некоторые миграции, но продолжаем запуск..."
    fi
else
    echo "✓ Все миграции применены!"
fi

# Создаем администратора (если нужно)
echo "=========================================="
echo "Проверка администратора..."
echo "=========================================="
if python manage.py ensure_admin 2>/dev/null; then
    echo "✓ Администратор проверен/создан."
else
    echo "⚠ Предупреждение: Команда ensure_admin не найдена или завершилась с ошибкой. Продолжаем запуск..."
fi

# Запускаем сервер
echo "=========================================="
echo "Запуск Django сервера..."
echo "=========================================="
exec python manage.py runserver 0.0.0.0:8000

