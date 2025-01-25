from django import forms
from .models import FreeContent


class FreeContentForm(forms.ModelForm):
    """Форма для создания и редактирования объекта модели FreeContent"""
    class Meta:
        model = FreeContent
        fields = ['title', 'body', 'video_link']

    def __init__(self, *args, **kwargs):

        super(FreeContentForm, self).__init__(*args, **kwargs)

        self.fields['title'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите название контента'
        })

        self.fields['body'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите содержание контента'
        })
