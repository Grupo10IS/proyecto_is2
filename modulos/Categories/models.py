from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=80,  blank=True)
    description = models.TextField(blank=True, null=True)
