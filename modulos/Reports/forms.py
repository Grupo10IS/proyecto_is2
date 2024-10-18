from django import forms
from django.forms import ModelForm

from .models import Report


class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "description"]  # Campos necesarios
        widgets = {
            "reason": forms.Select(attrs={"id": "id_reason"}),
            "description": forms.Textarea(
                attrs={"id": "id_description"}
            ),  # Oculta inicialmente la descripción
        }
