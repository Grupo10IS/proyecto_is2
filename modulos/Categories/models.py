from django.db import models


# Create your models here.
class Category(models.Model):
    """
    Modelo de categoría 'Category'.

    Este modelo representa una categoría con un nombre, descripción, estado y tipo.

    Attributes:
        name (CharField): Nombre de la categoría, con un máximo de 80 caracteres. Puede estar vacío.
        description (TextField): Descripción de la categoría. Puede estar vacío o ser nula.
        status (CharField): Estado de la categoría, con opciones definidas por `ESTADO_CHOICES`.
                            El valor predeterminado es 'ACTIVO'.
        tipo (CharField): Tipo de la categoría, con opciones definidas por `TIPO_CHOICES`.
                          El valor predeterminado es 'GRATIS'.

    Choices:
        ESTADO_CHOICES: Lista de opciones para el estado de la categoría, incluyendo 'ACTIVO' e 'INACTIVO'.
        TIPO_CHOICES: Lista de opciones para el tipo de la categoría, incluyendo 'PREMIUM' y 'GRATIS'.
    """

    ACTIVO = "Activo"
    INACTIVO = "Inactivo"

    PREMIUM = "Premium"
    GRATIS = "Gratis"

    ESTADO_CHOICES = [
        (ACTIVO, ACTIVO),
        (INACTIVO, INACTIVO),
    ]

    TIPO_CHOICES = [
        (PREMIUM, PREMIUM),
        (GRATIS, GRATIS),
    ]
    name = models.CharField(
        max_length=80, verbose_name="Nombre", blank=False, null=False
    )
    description = models.TextField(blank=True, null=True, verbose_name="Descricion")
    status = models.CharField(max_length=10, choices=ESTADO_CHOICES, default=ACTIVO)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default=GRATIS)

    # Campo nuevo para la imagen de la categoría
    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
        verbose_name="Imagen de la categoría",
    )

    def __str__(self):
        return self.name  # Returns the category name for display
