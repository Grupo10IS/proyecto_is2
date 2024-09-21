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

    title = models.CharField(max_length=80, verbose_name="Titulo")
    image = models.ImageField(
        upload_to="posts_images/", verbose_name="Portada", blank=True, null=True
    )
    content = MDTextField(name="content", verbose_name="Contenido")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=True, verbose_name="Categoria"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Status"
    )
    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    author = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, verbose_name="Autor"
    )
    tags = models.CharField(name="tags", max_length=80, blank=True, verbose_name="tags")

    favorites = models.ManyToManyField(
        UserProfile, related_name="favorite_posts", verbose_name="Favoritos"
    )
