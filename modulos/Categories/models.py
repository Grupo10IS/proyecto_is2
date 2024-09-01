from django.db import models


# Create your models here.
class Category:
    name = models.CharField(max_length=80, verbose_name="Nombre", blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descrición")
