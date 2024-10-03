from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from modulos.Posts.models import Log, Post
from modulos.UserProfile.models import UserProfile
from .models import Post
from django.db.models.signals import pre_save

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


@receiver(pre_save, sender=Post)
def send_notification_to_users(sender, instance, **kwargs):
    """
    Envía una notificación a los usuarios cuando un post cambia a estado "Publicado".
    """
    if instance.pk:
        # Obtenemos el estado anterior del post para verificar si el estado ha cambiado a "PUBLISHED"
        old_instance = Post.objects.filter(pk=instance.pk).first()

        if (
            old_instance
            and old_instance.status != Post.PUBLISHED
            and instance.status == Post.PUBLISHED
        ):

            category = instance.category

            recipients = UserProfile.objects.filter(
                receive_notifications=True,
            ).distinct()

            if category.tipo == category.PREMIUM:

                recipients = recipients.filter(
                    payment__category=category,
                    payment__status="completed",
                ).distinct()
            elif category.tipo == category.SUSCRIPCION:

                recipients = recipients.filter(
                    is_staff=False,
                    is_superuser=False,
                ).distinct()

            for recipient in recipients:

                subject = f"Nueva publicación en la categoría {category.name}💯💥"
                message = f"Hola {recipient.username}👋👋, hay una nueva publicación en la categoría {category.name}. No te la pierdas!, http://localhost:8000/posts/{instance.id}"

                send_mail(
                    subject,
                    message,
                    "groupmakex@gmail.com",
                    [recipient.email],
                    fail_silently=False,
                )


@receiver(pre_save, sender=Post)
def send_notification_to_authors(sender, instance, **kwargs):
    """
    Envía una notificación al autor cuando su post cambia de estado a "Publicado" o es "Rechazado".
    """
    if instance.pk:
        # Obtenemos el estado anterior del post para verificar los cambios
        old_instance = Post.objects.filter(pk=instance.pk).first()

        if old_instance:
            print(f"Signal ejecutado para el post: {instance.title}")
            print(f"Estado anterior: {old_instance.status}")
            print(f"Estado actual: {instance.status}")

            # Verificamos si hay un autor asignado al post
            author = instance.author
            if not author:
                print(
                    f"No se encontró un autor para el post {instance.title}. No se enviará notificación."
                )
                return

            print(f"Autor del post: {author.username}")
            print(f"Email del autor: {author.email}")

            # Notificar al autor si el estado cambió a "Publicado"
            if (
                old_instance.status != Post.PUBLISHED
                and instance.status == Post.PUBLISHED
            ):
                print(
                    f"El post {instance.title} ha sido publicado. Notificando al autor {author.username}."
                )
                subject = "Tu post ha sido publicado 🎉"
                message = f"Hola {author.username}, tu post '{instance.title}' ha sido publicado exitosamente. ¡Gracias por tu contribución!"
                send_mail(
                    subject,
                    message,
                    "groupmakex@gmail.com",
                    [author.email],
                    fail_silently=False,
                )
                print(
                    f"Correo enviado al autor {author.username} notificando la publicación."
                )

            # Notificar al autor si el post ha sido "Rechazado" (cambio a "Borrador")
            elif (
                old_instance.status in [Post.PENDING_REVIEW, Post.PENDING_PUBLICATION]
                and instance.status == Post.DRAFT
            ):
                print(
                    f"El post {instance.title} ha sido rechazado. Notificando al autor {author.username}."
                )
                subject = "Tu post ha sido rechazado 😕"
                message = (
                    f"Hola {author.username}, tu post '{instance.title}' ha sido rechazado y vuelto al estado de borrador. "
                    "Por favor, revisa los comentarios o haz los ajustes necesarios antes de volver a enviarlo para revisión."
                )
                send_mail(
                    subject,
                    message,
                    "groupmakex@gmail.com",
                    [author.email],
                    fail_silently=False,
                )
                print(
                    f"Correo enviado al autor {author.username} notificando el rechazo."
                )
