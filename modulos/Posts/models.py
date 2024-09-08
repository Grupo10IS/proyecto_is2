from django.db import models
from django.utils.timezone import now

from modulos.Categories.models import Category
from modulos.mdeditor.fields import MDTextField
from modulos.UserProfile.models import UserProfile


# Create your models here.
class Post(models.Model):
    DRAFT = "Borrador"
    PUBLISHED = "Publicado"
    REJECTED = "Rechazado"

    STATUS_CHOICES = [(DRAFT, DRAFT), (REJECTED, REJECTED), (PUBLISHED, PUBLISHED)]

    title = models.CharField(max_length=80)
    image = models.ImageField(upload_to="posts_images/", blank=True, null=True)
    content = MDTextField(name="content")
    category = models.ForeignKey(Category, on_delete=models.PROTECT, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    creation_date = models.DateTimeField(default=now)
    author = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)
    tags = models.CharField(name="tags", max_length=80, blank=True)
