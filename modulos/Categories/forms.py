from django import forms

from modulos.Categories.models import Category


class CategoryCreationForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "status", "tipo"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "tipo": forms.Select(attrs={"class": "form-control"}),
        }
