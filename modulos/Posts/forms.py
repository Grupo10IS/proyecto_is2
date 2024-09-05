from django import forms
from django.forms.models import ModelForm

from modulos.Posts.models import Post

class NewPostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "content"]

        widgets = {
            "title": forms.TextInput(
                attrs={"class": "custom-input", "placeholder": "Enter title"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "custom-textarea",
                    "rows": 5,
                    "placeholder": "Enter content",
                }
            ),
        }
