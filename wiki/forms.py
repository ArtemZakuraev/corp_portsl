from django import forms
from .models import WikiArticle, WikiImage, WikiFile, WikiViewGroup


class WikiArticleForm(forms.ModelForm):
    """Форма для создания и редактирования статьи базы знаний."""
    
    class Meta:
        model = WikiArticle
        fields = ['title', 'content', 'parent', 'order', 'is_published', 'visibility_type', 'view_groups']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название статьи'
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control wiki-editor',
                'rows': 25,
                'placeholder': 'Введите содержание статьи. Используйте панель инструментов для форматирования.'
            }),
            'parent': forms.Select(attrs={
                'class': 'form-control'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
            'is_published': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'visibility_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'toggleViewGroups()'
            }),
            'view_groups': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 5
            }),
        }
        help_texts = {
            'parent': 'Выберите родительскую статью, если эта статья является подразделом другой статьи.',
            'order': 'Число для сортировки статей в содержании (меньше = выше в списке).',
            'visibility_type': 'Выберите, кто может видеть эту статью.',
            'view_groups': 'Выберите группы пользователей (используется при выборе "Пользователи групп").',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        article = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Исключаем текущую статью и её дочерние статьи из списка возможных родителей
        if article and article.pk:
            exclude_ids = [article.pk]
            # Рекурсивно собираем все дочерние статьи
            def get_children_ids(art):
                ids = [art.pk]
                for child in art.children.all():
                    ids.extend(get_children_ids(child))
                return ids
            
            exclude_ids.extend(get_children_ids(article))
            self.fields['parent'].queryset = WikiArticle.objects.exclude(id__in=exclude_ids)
        else:
            self.fields['parent'].queryset = WikiArticle.objects.all()
        
        # Настройка queryset для групп просмотра
        self.fields['view_groups'].queryset = WikiViewGroup.objects.all().order_by('name')


class WikiViewGroupForm(forms.ModelForm):
    """Форма для создания и редактирования группы просмотра."""
    
    class Meta:
        model = WikiViewGroup
        fields = ['name', 'description', 'users']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название группы'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание группы (необязательно)'
            }),
            'users': forms.SelectMultiple(attrs={
                'class': 'form-control',
                'size': 10
            }),
        }
        help_texts = {
            'name': 'Уникальное название группы просмотра.',
            'description': 'Описание группы и её назначения.',
            'users': 'Выберите пользователей, которые будут входить в эту группу.',
        }


class WikiImageForm(forms.ModelForm):
    """Форма для загрузки изображения к статье."""
    
    class Meta:
        model = WikiImage
        fields = ['image', 'alt_text']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'alt_text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Описание изображения'
            }),
        }


class WikiFileForm(forms.ModelForm):
    """Форма для загрузки файла к статье."""
    
    class Meta:
        model = WikiFile
        fields = ['file', 'name', 'description']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название файла (необязательно)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание файла (необязательно)'
            }),
        }
