from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Define los roles
    ROLE_CHOICES = [
        ("suscriptor", "Suscriptor"),
        ("autor", "Autor"),
        ("editor", "Editor"),
        ("publicador", "Publicador"),
        ("administrador", "Administrador"),
    ]

    # Campo de correo electrónico único
    email = models.EmailField(unique=True, blank=False, null=False)

    # Campo de rol con sus opciones
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default="suscriptor")

    # Solucionar conflictos de reverse accessor con related_name
    groups = models.ManyToManyField("auth.Group", related_name="customuser_groups")
    user_permissions = models.ManyToManyField(
        "auth.Permission", related_name="customuser_user_permissions"
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
