from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Invitation, UserProfile


class InvitationCreateForm(forms.ModelForm):
    class Meta:
        model = Invitation
        fields = ["email_hint"]


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "last_name",
            "first_name",
            "middle_name",
            "department",
            "unit",
            "position",
            "phone_personal",
            "phone_internal",
            "photo",
            "manager",
        ]


class AdminUserCreateForm(UserCreationForm):
    """
    Форма для создания пользователя/администратора из раздела администрирования.
    """

    is_staff = forms.BooleanField(
        required=False,
        label="Администратор",
        help_text="Отметьте, если пользователь должен иметь права администратора портала.",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "is_staff")


class UserRoleEditForm(forms.ModelForm):
    """
    Форма для редактирования ролей пользователя (только для администраторов).
    Позволяет назначать модератора новостей и базы знаний.
    """

    is_news_moderator = forms.BooleanField(
        required=False,
        label="Модератор новостей",
        help_text="Пользователь сможет создавать и публиковать корпоративные новости.",
    )
    is_wiki_moderator = forms.BooleanField(
        required=False,
        label="Модератор базы знаний",
        help_text="Пользователь сможет создавать и редактировать статьи базы знаний.",
    )

    class Meta:
        model = UserProfile
        fields = ["is_news_moderator", "is_wiki_moderator"]


class UserThemeForm(forms.ModelForm):
    """
    Форма для настройки персональной темы портала.
    """

    theme_primary_color = forms.CharField(
        label="Основной цвет акцента",
        required=False,
        widget=forms.TextInput(attrs={"type": "color"}),
    )
    theme_sidebar_bg_color = forms.CharField(
        label="Цвет фона меню",
        required=False,
        widget=forms.TextInput(attrs={"type": "color"}),
    )
    theme_header_bg_color = forms.CharField(
        label="Цвет шапки",
        required=False,
        widget=forms.TextInput(attrs={"type": "color"}),
    )

    class Meta:
        model = UserProfile
        fields = [
            "theme_mode",
            "theme_primary_color",
            "theme_sidebar_bg_color",
            "theme_header_bg_color",
        ]


class MattermostSettingsForm(forms.ModelForm):
    """
    Форма для настройки авторизации Mattermost.
    """

    mattermost_password = forms.CharField(
        label="Пароль Mattermost",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
        help_text="Оставьте пустым, если не хотите менять пароль.",
    )

    class Meta:
        model = UserProfile
        fields = ["mattermost_username", "mattermost_password"]
        widgets = {
            "mattermost_username": forms.TextInput(attrs={"placeholder": "Логин для Mattermost"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Не показываем текущий пароль
        if self.instance and self.instance.pk:
            self.fields["mattermost_password"].help_text = "Оставьте пустым, если не хотите менять пароль."

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Получаем пароль из cleaned_data
        password = self.cleaned_data.get("mattermost_password")
        
        # Если пароль указан (не пустая строка), сохраняем его
        if password and password.strip():
            profile.mattermost_password = password.strip()
        else:
            # Если пароль не указан, сохраняем старый пароль из базы
            if self.instance and self.instance.pk:
                # Загружаем текущий профиль из базы, чтобы получить актуальный пароль
                try:
                    current_profile = UserProfile.objects.get(pk=self.instance.pk)
                    profile.mattermost_password = current_profile.mattermost_password
                except UserProfile.DoesNotExist:
                    profile.mattermost_password = ""
            else:
                profile.mattermost_password = ""
        
        if commit:
            profile.save()
        return profile


class SidebarSettingsForm(forms.ModelForm):
    """
    Форма для настройки размеров сайдбара (левого меню).
    """

    sidebar_width = forms.IntegerField(
        label="Ширина сайдбара (px)",
        min_value=200,
        max_value=500,
        help_text="Минимум: 200px, максимум: 500px",
        widget=forms.NumberInput(attrs={"step": 10, "min": 200, "max": 500}),
    )
    sidebar_height = forms.CharField(
        label="Высота сайдбара",
        max_length=50,
        help_text="Например: 600px или calc(100vh - 64px)",
        widget=forms.TextInput(attrs={"placeholder": "calc(100vh - 64px)"}),
    )

    class Meta:
        model = UserProfile
        fields = ["sidebar_custom_enabled", "sidebar_width", "sidebar_height"]
        widgets = {
            "sidebar_custom_enabled": forms.CheckboxInput(attrs={"onchange": "toggleSidebarSettings()"}),
        }


class CalDAVSettingsForm(forms.ModelForm):
    """
    Форма для настройки авторизации CalDAV.
    """

    caldav_password = forms.CharField(
        label="Пароль CalDAV",
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "Введите пароль"}),
        help_text="Оставьте пустым, если не хотите менять пароль.",
    )

    class Meta:
        model = UserProfile
        fields = ["caldav_email", "caldav_password"]
        widgets = {
            "caldav_email": forms.EmailInput(attrs={"placeholder": "Email для подключения к CalDAV"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Не показываем текущий пароль
        if self.instance and self.instance.pk:
            self.fields["caldav_password"].help_text = "Оставьте пустым, если не хотите менять пароль."

    def save(self, commit=True):
        profile = super().save(commit=False)
        # Получаем пароль из cleaned_data
        password = self.cleaned_data.get("caldav_password")
        
        # Если пароль указан (не пустая строка), сохраняем его
        if password and password.strip():
            profile.caldav_password = password.strip()
        else:
            # Если пароль не указан, сохраняем старый пароль из базы
            if self.instance and self.instance.pk:
                # Загружаем текущий профиль из базы, чтобы получить актуальный пароль
                try:
                    current_profile = UserProfile.objects.get(pk=self.instance.pk)
                    profile.caldav_password = current_profile.caldav_password
                except UserProfile.DoesNotExist:
                    profile.caldav_password = ""
            else:
                profile.caldav_password = ""
        
        if commit:
            profile.save()
        return profile



