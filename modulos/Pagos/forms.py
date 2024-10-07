from django import forms
from modulos.Pagos.models import Payment
from modulos.UserProfile.models import UserProfile
from modulos.Categories.models import Category
from django.contrib.auth import get_user_model

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

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False,
        label="Usuario",
        widget=forms.Select(attrs={"class": "form-control"}),
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
