from django import forms
from django.forms import ModelForm

from .models import Post  # Ensure you have imported the Post model


class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "content", "status", "tags"]

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
        }
