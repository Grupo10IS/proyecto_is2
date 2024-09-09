from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from modulos.Authorization import permissions
from modulos.UserProfile.models import UserProfile


class CustomRoleCreationForm(forms.ModelForm):
    perms = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=True,
        choices=permissions.permissions,
        label="Permisos",
    )

    class Meta:
        model = Group
        fields = ["name"]
