FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    ca-certificates \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Копируем и устанавливаем пользовательские SSL сертификаты
# Сначала копируем всю папку certs (может быть пустой)
COPY certs/ /tmp/certs/
# Затем копируем сертификаты, если они есть
RUN if [ -d /tmp/certs ] && [ "$(ls -A /tmp/certs 2>/dev/null)" ]; then \
        find /tmp/certs -name "*.crt" -exec cp {} /usr/local/share/ca-certificates/ \; 2>/dev/null || true; \
        find /tmp/certs -name "*.pem" -exec cp {} /usr/local/share/ca-certificates/ \; 2>/dev/null || true; \
        update-ca-certificates 2>/dev/null || true; \
    fi && \
    rm -rf /tmp/certs

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Делаем entrypoint.sh исполняемым
RUN chmod +x /app/entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=corp_portal.settings

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]


