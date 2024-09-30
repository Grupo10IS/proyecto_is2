from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Post
from modulos.UserProfile.models import UserProfile
from modulos.Authorization.permissions import user_has_access_to_category
from modulos.Pagos.models import Payment

from .models import Post


@receiver(post_save, sender=Post)
def send_notification_to_users(sender, instance, created, **kwargs):
    if created:
        # solo notificar los posts que sean publicados, no los borradores y demas
        if instance.status != Post.PUBLISHED:
            return

        category = instance.category

        # Filtrar usuarios que desean recibir notificaciones y tienen acceso a la categoría
        recipients = UserProfile.objects.filter(
            receive_notifications=True,  # Usuarios que desean recibir notificaciones
        ).distinct()

        # Filtrar usuarios que tienen acceso a la categoría del post
        if category.tipo == category.PREMIUM:
            recipients = recipients.filter(
                payment__category=category,
                payment__status="completed",  # Solo pagos completados
            ).distinct()
        elif category.tipo == category.SUSCRIPCION:
            recipients = recipients.filter(
                is_staff=False,  # Filtrar usuarios no administradores
                is_superuser=False,  # Filtrar superusuarios
            ).distinct()

        # Enviar un correo personalizado a cada destinatario
        for recipient in recipients:
            subject = f"Nueva publicación en la categoría {category.name}"
            message = f"Hola {recipient.username} 👋👋, hay una nueva publicación en la categoría {category.name}. No te la pierdas!, http://localhost:8000/posts/{instance.id}"

            send_mail(
                subject,
                message,
                "groupmakex@gmail.com",  # Dirección de remitente
                [recipient.email],  # Enviar a cada usuario individualmente
                fail_silently=False,
            )
