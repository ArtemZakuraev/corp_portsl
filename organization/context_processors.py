from .models import PortalSettings


def portal_settings(request):
    """
    Возвращает настройки портала (логотип, favicon) в шаблоны.
    Предполагается, что в базе всегда одна запись PortalSettings.
    """
    settings_obj = PortalSettings.get_solo()
    return {"portal_settings": settings_obj}










