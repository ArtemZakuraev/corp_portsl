# Скрипт PowerShell для генерации самоподписанного SSL сертификата для OnlyOffice

$CERT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$CERT_FILE = Join-Path $CERT_DIR "onlyoffice.crt"
$KEY_FILE = Join-Path $CERT_DIR "onlyoffice.key"

# Проверяем наличие OpenSSL
$opensslPath = Get-Command openssl -ErrorAction SilentlyContinue

if (-not $opensslPath) {
    Write-Error "OpenSSL не найден. Установите OpenSSL или используйте mkcert."
    exit 1
}

# Генерируем самоподписанный сертификат
& openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
    -keyout "$KEY_FILE" `
    -out "$CERT_FILE" `
    -subj "/C=RU/ST=Moscow/L=Moscow/O=CorpPortal/OU=IT/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,DNS:127.0.0.1,IP:127.0.0.1"

if ($LASTEXITCODE -eq 0) {
    Write-Host "SSL сертификат создан:" -ForegroundColor Green
    Write-Host "  Certificate: $CERT_FILE"
    Write-Host "  Private Key: $KEY_FILE"
    Write-Host ""
    Write-Host "Для установки доверия к сертификату в Windows выполните:" -ForegroundColor Yellow
    Write-Host "  Import-Certificate -FilePath '$CERT_FILE' -CertStoreLocation Cert:\CurrentUser\Root"
} else {
    Write-Error "Ошибка при генерации сертификата"
    exit 1
}



