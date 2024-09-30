from django.db import models
from django.utils.timezone import now

from modulos.Categories.models import Category
from modulos.mdeditor.fields import MDTextField
from modulos.UserProfile.models import UserProfile


# Create your models here.
class Post(models.Model):
    DRAFT = "Borrador"
    PENDING_REVIEW = "Esperando revision"
    PENDING_PUBLICATION = "Esperando publicacion"
    PUBLISHED = "Publicado"
    INACTIVE = "INACTIVE"

    STATUS_CHOICES = [
        (DRAFT, DRAFT),
        (PENDING_REVIEW, PENDING_REVIEW),
        (PENDING_PUBLICATION, PENDING_PUBLICATION),
        (PUBLISHED, PUBLISHED),
        (INACTIVE, INACTIVE),
    ]

    title = models.CharField(max_length=80, verbose_name="Titulo")
    image = models.ImageField(
        upload_to="posts_images/", verbose_name="Portada", blank=True, null=True
    )
    content = MDTextField(name="content", verbose_name="Contenido")
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, null=False, verbose_name="Categoria"
    )
    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default=DRAFT, verbose_name="Status"
    )
    creation_date = models.DateTimeField(default=now, verbose_name="Fecha de creacion")
    publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion"
    )
    scheduled_publication_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de publicacion agendada"
    )
    author = models.ForeignKey(
        UserProfile, on_delete=models.SET_NULL, null=True, verbose_name="Autor"
    )
    # FIX: repensar el tema de los tags
    tags = models.CharField(name="tags", max_length=80, blank=True, verbose_name="tags")

    favorites = models.ManyToManyField(
        UserProfile, related_name="favorite_posts", verbose_name="Favoritos"
    )
