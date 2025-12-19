# Тестирование SSL сертификата OnlyOffice

## Проверка доступности OnlyOffice API

### Из браузера:

1. Откройте в браузере: `https://localhost/web-apps/apps/api/documents/api.js`
   (Порт 443 - стандартный HTTPS порт, не требуется в URL)
   - Если браузер показывает предупреждение о недоверенном сертификате, нажмите "Дополнительно" и "Продолжить"
   - Должен загрузиться JavaScript файл

2. Установите сертификат в доверенные (чтобы избежать предупреждений):
   ```powershell
   # Запустите от имени администратора:
   .\certificates\install-cert.ps1
   ```
   
   Или вручную:
   ```powershell
   Import-Certificate -FilePath "certificates\onlyoffice.crt" -CertStoreLocation Cert:\LocalMachine\Root
   ```

### Из контейнера web (Python):

```python
import urllib.request
import ssl

# Используем контекст SSL с игнорированием проверки сертификата
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Или используем системные доверенные сертификаты (после установки)
ctx = ssl.create_default_context()

url = 'https://localhost/web-apps/apps/api/documents/api.js'
req = urllib.request.Request(url)
resp = urllib.request.urlopen(req, context=ctx)
print('Status:', resp.status)
print('Content-Length:', resp.headers.get('Content-Length'))
```

### Из контейнера nginx:

```bash
docker-compose exec onlyoffice_nginx wget -O- --no-check-certificate https://localhost/web-apps/apps/api/documents/api.js | head -20
```

## Проверка SSL сертификата

```bash
# Просмотр информации о сертификате
openssl s_client -connect localhost:443 -showcerts < /dev/null 2>/dev/null | openssl x509 -noout -text
```

## Решение проблем

### Проблема: Браузер блокирует самоподписанный сертификат
**Решение:** Установите сертификат в доверенные (см. выше)

### Проблема: CORS ошибка
**Решение:** Проверьте настройки CORS в nginx/nginx.conf

### Проблема: 404 Not Found
**Решение:** 
1. Проверьте, что OnlyOffice запущен: `docker-compose ps onlyoffice`
2. Проверьте логи: `docker-compose logs onlyoffice --tail 50`
3. Проверьте nginx конфигурацию: `docker-compose exec onlyoffice_nginx nginx -t`

### Проблема: Connection refused
**Решение:**
1. Проверьте, что nginx запущен: `docker-compose ps onlyoffice_nginx`
2. Проверьте, что порт 443 проброшен: `docker-compose ps onlyoffice_nginx`
3. Проверьте логи: `docker-compose logs onlyoffice_nginx --tail 50`

