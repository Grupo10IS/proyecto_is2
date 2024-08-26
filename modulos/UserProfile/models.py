from django.contrib.auth.models import AbstractUser, Group
from django.db import models

# Create your models here.


class UserProfile(AbstractUser):
    direccion = models.CharField(max_length=80, verbose_name="direccion", blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
