from django import forms
from django.forms import CharField, Form, ModelForm

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
        }


class SearchPostForm(Form):
    input = CharField(
        max_length=120,
        widget=forms.TextInput(
            attrs={
                "class": "form-control-sm",
                "id": "search-input",
                "placeholder": "Search ...",
                "aria-label": "Search",
                "style": "display: none",
            }
        ),
    )
