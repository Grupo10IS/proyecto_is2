from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Create your models here.

class UserProfile(AbstractUser):
    direccion = "que ondaaa"
