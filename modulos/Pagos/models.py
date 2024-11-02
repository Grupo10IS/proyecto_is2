from django.conf import settings
from django.db import models
from django.utils import timezone

from modulos.Categories.models import \
    Category  # Importa tu modelo de categoría

# Definimos los métodos de pago disponibles
PAYMENT_METHODS = [
    ("credit_card", "Tarjeta de Crédito"),
    ("debit_card", "Tarjeta de Débito"),
]

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2, default=1.00)
    date_paid = models.DateTimeField(default=timezone.now)
    stripe_payment_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=20, default="pending")

    # Campos adicionales para almacenar detalles de la tarjeta
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHODS, default="credit_card"
    )
    funding_type = models.CharField(
        max_length=10, null=True, blank=True
    )  # "credit", "debit", "prepaid", o "unknown"
    card_brand = models.CharField(
        max_length=20, null=True, blank=True
    )  # Marca de la tarjeta, como "visa", "mastercard"
    last4 = models.CharField(
        max_length=4, null=True, blank=True
    )  # Últimos 4 dígitos de la tarjeta

    def __str__(self):
        return f"Payment {self.user.username} for {self.category.name}"
