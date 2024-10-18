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
    profile_image = models.ImageField(
        upload_to="profile_images/",
        blank=True,
        null=True,
        verbose_name="Foto de perfil",
    )

    # estadisticas del publicador
    c_creados = models.IntegerField(default=0)
    c_aprobados = models.IntegerField(default=0)
    c_publicados = models.IntegerField(default=0)
    c_rechazados = models.IntegerField(default=0)

    # estadisticas del editor y publicador
    c_audit_revisados = models.IntegerField(default=0)
    c_audit_publicados = models.IntegerField(default=0)
    c_audit_rechazados = models.IntegerField(default=0)  # rechazo por parte del publicador

    # estadisticas de admin
    c_audit_eliminados = models.IntegerField(default=0)

    def has_perm(self, perm: str, obj=None) -> bool:
        return super().has_perm("UserProfile." + perm, obj)
