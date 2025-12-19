# SSL Сертификаты для OnlyOffice

## Генерация сертификата

Для генерации самоподписанного SSL сертификата для OnlyOffice выполните:

```bash
docker-compose --profile cert run --rm cert_generator
```

Это создаст два файла в папке `certificates/`:
- `onlyoffice.crt` - SSL сертификат
- `onlyoffice.key` - приватный ключ

**ВАЖНО:** После генерации сертификата обязательно установите его в доверенные сертификаты Windows, иначе браузер будет блокировать загрузку OnlyOffice API.

## Установка доверия к сертификату (Windows)

### Быстрый способ (рекомендуется):

1. Откройте PowerShell от имени администратора
2. Выполните:
   ```powershell
   .\certificates\install-cert.ps1
   ```
3. Перезапустите браузер

### Ручная установка:

Для того чтобы браузер доверял самоподписанному сертификату, нужно добавить его в хранилище доверенных корневых сертификатов:

### PowerShell (от имени администратора):

```powershell
Import-Certificate -FilePath "certificates\onlyoffice.crt" -CertStoreLocation Cert:\LocalMachine\Root
```

### Или через mmc.exe:

1. Откройте `mmc.exe`
2. Файл -> Добавить или удалить оснастку
3. Добавьте "Сертификаты" -> Компьютер (локальный)
4. Откройте "Доверенные корневые центры сертификации" -> Сертификаты
5. Действия -> Все задачи -> Импорт
6. Выберите `certificates\onlyoffice.crt`
7. Следуйте инструкциям мастера импорта

## Альтернатива: использование mkcert

Для более удобной работы с локальными сертификатами можно использовать [mkcert](https://github.com/FiloSottile/mkcert):

```bash
# Установка mkcert
# Windows: choco install mkcert
# или скачать с https://github.com/FiloSottile/mkcert/releases

# Создание локального CA
mkcert -install

# Генерация сертификата
mkcert -key-file certificates/onlyoffice.key -cert-file certificates/onlyoffice.crt localhost 127.0.0.1
```

Сертификаты, созданные через mkcert, автоматически доверяются системой и браузерами.

