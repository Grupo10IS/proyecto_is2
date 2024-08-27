from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.


class UserProfile(AbstractUser):
    email = models.EmailField(unique=True, blank=False, null=False)
