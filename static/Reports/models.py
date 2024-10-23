from django.db import models

from modulos.Posts.models import Post
from modulos.UserProfile.models import UserProfile


class Report(models.Model):
    REASON_CHOICES = [
        ("SPAM", "Spam"),
        ("CONTENIDO_INAPROPIADO", "Contenido inapropiado"),
        ("VIOLENCIA", "Violencia"),
        ("DISCRIMINACION", "Discriminación"),
        ("OTRO", "Otro"),
    ]

    content = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reports")
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE
    )  # Usuario que hizo el reporte
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(
        blank=True, null=True
    )  # Descripción opcional del reporte
    creation_date = models.DateTimeField(
        auto_now_add=True
    )  # fecha y hora de creacion del reporte
    is_handled = models.BooleanField(default=False)  # si el reporte fue  tratado o no
