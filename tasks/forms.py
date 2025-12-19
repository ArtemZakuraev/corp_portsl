from django import forms

from .models import Task
from .utils import get_user_subordinates


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "description", "assignee_email", "due_date", "priority"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }


class SelfTaskForm(forms.ModelForm):
    """
    Форма для постановки задач самому себе (раздел «Мои задачи»).
    """

    class Meta:
        model = Task
        fields = ["title", "description", "due_date", "priority"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }


class SubordinateTaskForm(forms.ModelForm):
    """
    Форма для создания задачи подчиненному.
    """
    
    assignee = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label="Исполнитель",
        help_text="Выберите сотрудника из ваших подчиненных.",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    
    class Meta:
        model = Task
        fields = ["title", "description", "assignee", "due_date", "priority"]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "priority": forms.Select(attrs={"class": "form-control"}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Устанавливаем queryset для выбора подчиненных
            subordinates = get_user_subordinates(user)
            self.fields['assignee'].queryset = subordinates

