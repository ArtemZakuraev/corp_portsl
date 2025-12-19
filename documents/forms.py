from django import forms

from .models import Document


class DocumentUploadForm(forms.ModelForm):
    file = forms.FileField(label="Файл")

    class Meta:
        model = Document
        fields = ["name", "description", "access_level", "assigned_users"]










