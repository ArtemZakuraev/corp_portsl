#!/bin/bash
# Скрипт для генерации самоподписанного SSL сертификата для OnlyOffice

CERT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CERT_FILE="$CERT_DIR/onlyoffice.crt"
KEY_FILE="$CERT_DIR/onlyoffice.key"

# Генерируем самоподписанный сертификат
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$KEY_FILE" \
    -out "$CERT_FILE" \
    -subj "/C=RU/ST=Moscow/L=Moscow/O=CorpPortal/OU=IT/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"

echo "SSL сертификат создан:"
echo "  Certificate: $CERT_FILE"
echo "  Private Key: $KEY_FILE"
echo ""
echo "Для Windows PowerShell используйте generate-cert.ps1"



