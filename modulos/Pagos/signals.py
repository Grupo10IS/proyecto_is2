from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from modulos.Pagos.models import Payment


# Este decorador define una función que será ejecutada cuando se emita la señal post_save para el modelo Payment.
@receiver(post_save, sender=Payment)
def send_payment_notification(sender, instance, created, **kwargs):
    """
    Envía una notificación por correo electrónico cuando un pago es completado exitosamente.
    """
    # Verificar si el estado del pago es 'completed' y si el objeto ha sido actualizado, no creado
    if instance.status == "completed" and not created:
        user_email = instance.user.email
        category_name = instance.category.name

        # Configurar el asunto y el mensaje del correo
        subject = f"Compra exitosa de la categoría premium {category_name}"
        message = (
            f"Hola {instance.user.username}👋👋,\n\n"
            f"Gracias por comprar el acceso a la categoría premium '{category_name}'.\n"
            f"Ahora puedes acceder a los contenidos exclusivos de esta categoría en nuestro sitio!\n\n"
            f"¡Gracias por tu compra!😁😁\n"
            f"Saludos👋,\nEl equipo de MakeX"
        )

        # Enviar el correo electrónico
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,  # Dirección de correo de origen configurada en settings.py
            [user_email],  # Correo del destinatario (usuario que hizo la compra)
            fail_silently=False,
        )
