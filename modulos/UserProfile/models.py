from django.contrib.auth.models import AbstractUser
from django.db import models

from modulos.Categories.models import Category
from modulos.Pagos.models import Payment

# Create your models here.


class UserProfile(AbstractUser):
    address = models.CharField(max_length=80, verbose_name="Dirección", blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(
        max_length=15, verbose_name="Número de teléfono", blank=True
    )
    pagos = models.ManyToManyField(Category, through=Payment, related_name="users_paid")
    receive_notifications = models.BooleanField(
        default=False,
        verbose_name="Desea recibir notificaciones sobre nuevas publicaciones?",
    )

    def has_perm(self, perm: str, obj=None) -> bool:
        return super().has_perm("UserProfile." + perm, obj)
