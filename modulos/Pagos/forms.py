from django import forms
from django.contrib.auth import get_user_model

from modulos.Categories.models import Category
from modulos.Pagos.models import Payment
from modulos.UserProfile.models import UserProfile


# Formulario para la información de pago
# Formulario para la información de pago
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["amount"]  # El campo de monto de pago
        widgets = {
            "amount": forms.HiddenInput()  # Oculto porque el monto siempre será $5 (o el que sea)
        }


# Formulario para mostrar el perfil del usuario, con datos autocompletados


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["username", "email"]  # Agregamos username y email
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }


User = get_user_model()


# Formulario para el filtrado de pagos por categoría, usuario y fechas


class PaymentFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Categoría",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    user = forms.CharField(
        required=False,
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Escribe el nombre del usuario...",
            }
        ),
    )

    date_from = forms.DateField(
        required=False,
        label="Fecha desde",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    date_to = forms.DateField(
        required=False,
        label="Fecha hasta",
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )

    # Filtros adicionales para tarjeta
    card_brand = forms.ChoiceField(
        choices=[
            ("", "Todas"),  # Opción para seleccionar todas las marcas
            ("visa", "Visa"),
            ("mastercard", "MasterCard"),
            ("amex", "American Express"),
            ("discover", "Discover"),
        ],
        required=False,
        label="Marca de Tarjeta",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    funding_type = forms.ChoiceField(
        choices=[
            ("", "Todos"),
            ("credit", "Crédito"),
            ("debit", "Débito"),
            ("unknown", "Desconocido"),
        ],
        required=False,
        label="Tipo de Tarjeta",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
