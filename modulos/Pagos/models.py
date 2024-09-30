from django.conf import settings
from django.db import models
from django.utils import timezone
from modulos.Categories.models import Category  # Importa tu modelo de categoría


class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    date_paid = models.DateTimeField(default=timezone.now)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")  # Agregar este campo

    def __str__(self):
        return f"Payment {self.user.username} for {self.category.name}"
