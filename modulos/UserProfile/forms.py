from django import forms
from django.contrib.auth.forms import (PasswordResetForm, UserChangeForm,
                                       UserCreationForm)
from django.contrib.auth.models import Group

from .models import UserProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "password1": forms.PasswordInput(attrs={"class": "form-control"}),
            "password2": forms.PasswordInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if UserProfile.objects.filter(username=username).exists():
            raise forms.ValidationError("Este username ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo está ya en uso")
        return email


class UserGroupForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Grupos",
    )

    class Meta:
        model = UserProfile
        fields = ["username", "email", "groups"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = UserProfile
        fields = ["username", "email"]


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone_number", "address"]


class CustomPasswordResetForm(PasswordResetForm):

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not UserProfile.objects.filter(email=email).exists():
            raise forms.ValidationError("Correo no asociado a una cuenta")
        return email

    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.html",
        use_https=False,
        token_generator=None,
        from_email=None,
        request=None,
        html_email_template_name=None,
        extra_email_context=None,
    ):
        """
        Envía un correo con las instrucciones para restablecer la contraseña.
        """
        email = self.cleaned_data["email"]
        users = UserProfile.objects.filter(email=email)
        if users.exists():
            for user in users:
                super().save(
                    domain_override=domain_override,
                    subject_template_name=subject_template_name,
                    email_template_name=email_template_name,
                    use_https=use_https,
                    token_generator=token_generator,
                    from_email=from_email,
                    request=request,
                    html_email_template_name=html_email_template_name,
                    extra_email_context=extra_email_context,
                )
