from django.db import models

from modulos.Categories.models import Category


# Create your models here.
class Post(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Borrador"),
        ("PUBLISHED", "Publicado"),
        ("REJECTED", "Rechazado"),
    ]

    title = models.CharField(max_length=80)
    content = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="DRAFT")
    # creation_date = models.DateTimeField(default=timezone.now)

    """
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comments = models.ManyToManyField(
        "Comment", related_name="posts"
    )  # Relación muchos a muchos con el modelo Comment
    history = models.ManyToManyField(
        "ContentHistory", related_name="posts"
    )  # Relación muchos a muchos con el modelo ContentHistory
    """