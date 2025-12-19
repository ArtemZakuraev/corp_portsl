# Скрипт для установки SSL сертификата OnlyOffice в доверенные корневые сертификаты Windows

$certPath = Join-Path $PSScriptRoot "onlyoffice.crt"

if (-not (Test-Path $certPath)) {
    Write-Error "Сертификат не найден: $certPath"
    Write-Host "Сначала создайте сертификат: docker-compose --profile cert run --rm cert_generator"
    exit 1
}

Write-Host "Установка SSL сертификата OnlyOffice в доверенные корневые сертификаты..." -ForegroundColor Yellow
Write-Host "Сертификат: $certPath" -ForegroundColor Gray

# Проверяем, запущен ли скрипт от имени администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warning "Для установки сертификата требуются права администратора."
    Write-Host "Перезапускаю скрипт от имени администратора..." -ForegroundColor Yellow
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

try {
    # Импортируем сертификат в хранилище LocalMachine\Root (требуются права администратора)
    Import-Certificate -FilePath $certPath -CertStoreLocation Cert:\LocalMachine\Root -ErrorAction Stop
    
    Write-Host "Сертификат успешно установлен!" -ForegroundColor Green
    Write-Host "Теперь браузер будет доверять SSL сертификату OnlyOffice." -ForegroundColor Green
    Write-Host ""
    Write-Host "Примечание: Возможно потребуется перезапустить браузер для применения изменений." -ForegroundColor Yellow
} catch {
    Write-Error "Ошибка при установке сертификата: $_"
    exit 1
}



