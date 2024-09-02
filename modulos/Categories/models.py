from django.db import models


# Create your models here.
class Category(models.Model):
    ESTADO_CHOICES = [
        ("ACTIVO", "Activo"),
        ("INACTIVO", "Inactivo"),
    ]

    TIPO_CHOICES = [
        ("PREMIUM", "Premium"),
        ("GRATIS", "Gratis"),
    ]
    name = models.CharField(max_length=80, verbose_name="Nombre", blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descrición")
    status = models.CharField(max_length=10, choices=ESTADO_CHOICES, default="ACTIVO")
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default="GRATIS")
