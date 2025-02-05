from django import forms
from .models import FreeContent, PaidContent


class FreeContentForm(forms.ModelForm):
    """Форма для создания и редактирования объекта модели FreeContent"""

    class Meta:
        model = FreeContent
        fields = ["title", "body", "video_link"]

    def __init__(self, *args, **kwargs):

        super(FreeContentForm, self).__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите название контента"}
        )

        self.fields["body"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите содержание контента"}
        )


class PaidContentForm(forms.ModelForm):
    """Форма для создания и редактирования объекта модели PaidContent"""

    class Meta:
        model = PaidContent
        fields = ["title", "body", "video_link", "price"]

    def __init__(self, *args, **kwargs):

        super(PaidContentForm, self).__init__(*args, **kwargs)

        self.fields["title"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите название контента"}
        )

        self.fields["body"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите содержание контента"}
        )

        self.fields["price"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Введите цену доступа к контенту"}
        )
