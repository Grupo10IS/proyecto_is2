from django import forms

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
