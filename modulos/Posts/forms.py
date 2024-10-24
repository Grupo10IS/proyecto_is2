from django import forms
from django.forms import CharField, Form, ModelForm

from modulos.Categories.models import Category

from .models import Post  # Ensure you have imported the Post model


class NewPostForm(ModelForm):
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
            "category": forms.Select(
                attrs={"class": "custom-select"}  # Custom class for the dropdown
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "custom-textarea",
                    "rows": 5,
                    "placeholder": "Enter content",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "custom-file-input"}  # Custom class for the file input
            ),
            "publication_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            ),
            "expiration_date": forms.DateInput(
                attrs={"type": "date", "class": "custom-date-input"}
            ),
        }


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
