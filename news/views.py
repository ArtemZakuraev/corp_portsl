from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from django.conf import settings

from accounts.models import UserProfile
from .models import News, NewsImage


def _is_news_moderator(user) -> bool:
    if not user.is_authenticated:
        return False
    try:
        return bool(user.profile.is_news_moderator)
    except UserProfile.DoesNotExist:
        return False


@login_required
def news_list(request):
    """
    Лента новостей компании с возможностью публикации для модераторов.
    """
    news_items = News.objects.prefetch_related("images").all()
    is_moderator = _is_news_moderator(request.user)
    return render(
        request,
        "news/news_list.html",
        {
            "news_items": news_items,
            "is_moderator": is_moderator,
        },
    )


@login_required
def news_create(request):
    """
    Создание новости модератором.
    После сохранения последняя новость отправляется всем сотрудникам по email.
    """
    if not _is_news_moderator(request.user):
        return redirect("news_list")

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        body = request.POST.get("body", "").strip()
        uploaded_files = request.FILES.getlist("images")

        if title and body:
            news = News.objects.create(title=title, body=body, author=request.user)

            # Обработка загруженных изображений
            for uploaded_file in uploaded_files:
                # Проверка типа файла
                if uploaded_file.content_type.startswith("image/"):
                    alt_text = uploaded_file.name.rsplit(".", 1)[0] if "." in uploaded_file.name else uploaded_file.name
                    NewsImage.objects.create(
                        news=news,
                        image=uploaded_file,
                        alt_text=alt_text,
                    )

            # Рассылка последней новости всем активным пользователям
            recipients = list(
                User.objects.filter(is_active=True)
                .exclude(email="")
                .values_list("email", flat=True)
            )
            if recipients:
                subject = f"Новая новость: {news.title}"
                # В письме шлём текст без HTML (простое содержимое)
                message = f"{news.title}\n\n{news.body}"
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    recipients,
                    fail_silently=True,
                )

            return redirect("news_list")

        # простая валидация: если не заполнено, остаёмся на форме
        context = {
            "title_value": title,
            "body_value": body,
            "error": "Пожалуйста, заполните тему и текст новости.",
        }
    else:
        context = {}

    return render(request, "news/news_create.html", context)
