from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserProfile(AbstractUser):
    """
    Modelo de perfil de usuario 'UserProfile'.

    Este modelo extiende de `AbstractUser` para agregar campos adicionales al perfil del usuario.
    Incluye campos para dirección, correo electrónico y número de teléfono.

    Attributes:
        address (CharField): Dirección del usuario, con un máximo de 80 caracteres. Puede estar vacío.
        email (EmailField): Correo electrónico del usuario, que debe ser único y no puede estar vacío.
        phone_number (CharField): Número de teléfono del usuario, con un máximo de 15 caracteres. Puede estar vacío.
    """

    address = models.CharField(max_length=80, verbose_name="Dirección", blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(
        max_length=15, verbose_name="Número de teléfono", blank=True
    )
