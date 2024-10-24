from django import forms
from django.core.exceptions import ValidationError
from django.forms import CharField, Form, ModelForm

from modulos.Categories.models import Category

from .models import Post  # Ensure you have imported the Post model


# Formulario para modales de confirmacion con mensaje
class ModalWithMsgForm(forms.Form):
    msg = forms.CharField(widget=forms.Textarea, label="", required=True)


class NewPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            "title",
            "image",
            "category",
            "tags",
            "content",
            "publication_date",
            "expiration_date",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "custom-input", "placeholder": "Enter title"}
            ),
            "tags": forms.TextInput(
                attrs={"class": "custom-input", "placeholder": "Tag1, tag2, tag3 ..."}
            ),
            "category": forms.Select(attrs={"class": "custom-select"}),
            "content": forms.Textarea(
                attrs={
                    "class": "custom-textarea",
                    "rows": 5,
                    "placeholder": "Enter content",
                }
            ),
            "image": forms.ClearableFileInput(attrs={"class": "custom-file-input"}),
            "publication_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            ),
            "publication_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            )
        }

    # Desactivar validación implícita `required` en estos campos
    title = forms.CharField(required=False)
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    image = forms.ImageField(required=False)

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if not title:
            raise ValidationError("Título requerido.")  # Mensaje personalizado
        return title

    def clean_category(self):
        category = self.cleaned_data.get("category")
        if not category:
            raise ValidationError("Categoría requerida.")  # Mensaje personalizado
        return category

    def clean_content(self):
        content = self.cleaned_data.get("content")
        if not content:
            raise ValidationError("Contenido requerido.")  # Mensaje personalizado
        return content


class SearchPostForm(forms.Form):
    input = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control-sm",
                "id": "search-input",
                "placeholder": "Buscar por título o contenido...",
                "aria-label": "Search",
                "style": "width: 50%;",
            }
        ),
        label="Buscar",
    )


class PostsListFilter(forms.Form):
    input = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control-sm",
                "id": "search-input",
                "placeholder": "Buscar por título o contenido...",
                "aria-label": "Search",
                "style": "width: 50%;",
            }
        ),
        label="Buscar",
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-control-sm"}),
        label="Categoría",
    )
    author = forms.CharField(
        max_length=120,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control-sm",
                "placeholder": "Autor...",
            }
        ),
        label="Autor",
    )
    publication_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control-sm"}),
        label="Fecha de Publicación",
    )
