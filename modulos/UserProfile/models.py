from django.contrib.auth.models import AbstractUser, Group
from django.db import models

# Create your models here.


class UserProfile(AbstractUser):
    address = models.CharField(max_length=80, verbose_name="Dirección", blank=True)
    email = models.EmailField(unique=True, blank=False, null=False)
    phone_number = models.CharField(
        max_length=15, verbose_name="Número de teléfono", blank=True
    )
    # profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  # Comentado temporalmente
