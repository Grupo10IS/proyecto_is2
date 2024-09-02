from django.db import models


# Create your models here.
<<<<<<< HEAD
class Category:
    name = models.CharField(max_length=80, verbose_name="Nombre", blank=True)
    description = models.TextField(blank=True, null=True, verbose_name="Descrición")
=======
class Category(models.Model):
    name = models.CharField(max_length=80,  blank=True)
    description = models.TextField(blank=True, null=True)
>>>>>>> categories
