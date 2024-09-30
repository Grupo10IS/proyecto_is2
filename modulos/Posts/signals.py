from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from modulos.Posts.models import Log, Post
from modulos.UserProfile.models import UserProfile

from .models import Post


@receiver(post_save, sender=Post)
def log_post_change(sender, instance, **kwargs):
    """
    Señal para generar un nuevo log con cada accion que se realiza sobre un post.

    Todas las acciones sobre el contenido seran reporatadas y generaran un nuevo log el
    cual contendra la fecha de la accion, la accion en si, el campo donde se realizo la actualizacion
    y el usuario que la realizo.
    """
    if not instance.pk:
        Log(post=instance, message="Post creado").save()
        return

    old_instance = sender.objects.get(pk=instance.pk)

    changes = ""
    for field in instance._meta.fields:
        field_name = field.name
        old_value = getattr(old_instance, field_name)
        new_value = getattr(instance, field_name)
        if old_value != new_value:
            if field_name != "version":
                changes += f"Campo {field_name} actualizado.\n"

    if changes != "":
        print(changes)
        Log(post=instance, message=changes).save()


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
