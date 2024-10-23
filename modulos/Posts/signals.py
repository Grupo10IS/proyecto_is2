from django.core.mail import send_mail
from django.db.models import Count
from django.db.models.signals import m2m_changed, post_save, pre_save
from django.dispatch import receiver

from modulos.Posts.models import Log, Post
from modulos.UserProfile.models import UserProfile

from .models import Post


@receiver(pre_save, sender=Post)
def send_notification_to_users(sender, instance, **kwargs):
    """
    Envía una notificación a los usuarios cuando un post cambia a estado "Publicado".
    """
    if instance.pk:
        old_instance = Post.objects.filter(pk=instance.pk, active=True).first()

        # Verificar si se realiza un cambio de estado a "PUBLISHED"
        if (
            old_instance
            and old_instance.status != Post.PUBLISHED
            and instance.status == Post.PUBLISHED
        ):

            category = instance.category

            users = UserProfile.objects.filter(
                receive_notifications=True,
            ).distinct()

            if category.tipo == category.PREMIUM:
                users = users.filter(
                    payment__category=category,
                    payment__status="completed",
                ).distinct()

            elif category.tipo == category.SUSCRIPCION:
                users = users.filter(
                    is_staff=False,
                    is_superuser=False,
                ).distinct()

            for recipient in users:
                subject = f"Nueva publicación en la categoría {category.name}💯💥"
                message = f"Hola {recipient.username}👋👋, hay una nueva publicación en la categoría {category.name}. No te la pierdas!, https://www.makexfp.com/posts/{instance.id}"

                try:
                    send_mail(
                        subject,
                        message,
                        "groupmakex@gmail.com",
                        [recipient.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print("Ocurrieron errores al notificar a los usuarios: ", e)
                    return


# NOTIFICA A LOS AUTORES CUANDO SU POST ES PUBLICADO


@receiver(pre_save, sender=Post)
def send_notification_to_authors(sender, instance, **kwargs):
    """
    Envía una notificación al autor cuando su post cambia de estado a "Publicado".
    """
    if instance.pk:
        # Obtenemos el estado anterior del post para verificar los cambios
        old_instance = Post.objects.filter(pk=instance.pk, active=True).first()

        if old_instance:
            # Verificamos si hay un autor asignado al post
            author = instance.author
            if not author:
                print(
                    f"No se encontró un autor para el post {instance.title}. No se enviará notificación."
                )
                return

            # Notificar al autor si el estado cambió a "Publicado"
            if (
                old_instance.status != Post.PUBLISHED
                and instance.status == Post.PUBLISHED
            ):
                subject = "Tu post ha sido publicado 🎉"
                message = f"Hola {author.username}, tu post '{instance.title}' ha sido publicado exitosamente. ¡Gracias por tu contribución!"

                try:
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
                except Exception as e:
                    print("Ocurrieron errores al notificar al autor del post: ", e)
                    return


# NOTIFICA A LOS AUTORES CUANDO SU POST ESTA NUMERO 1 O ENTRE LOS 5 MAS POPULARES


def check_top_posts():
    """
    Obtiene el post con más favoritos y los 5 posts más populares.
    Retorna el post destacado y una lista con los 5 posts más populares.
    """
    # Obtener el post destacado (más favoritos)
    post_destacado = (
        Post.objects.filter(status=Post.PUBLISHED, active=True)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")
        .first()
    )

    # Obtener los 5 posts más populares
    posts_populares = (
        Post.objects.filter(status=Post.PUBLISHED, active=True)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")[:5]
    )

    return post_destacado, posts_populares


@receiver(post_save, sender=Post)
@receiver(m2m_changed, sender=Post.favorites.through)
def notify_top_posts(sender, instance, **kwargs):
    """
    Verifica si un post se convierte en destacado o entra al Top 5 posts más populares,
    y envía una notificación al autor del post.

    También cuando se cambian los favoritos.
    """
    # Verificar el top 5 y el post destacado
    post_destacado, posts_populares = check_top_posts()

    author = instance.author
    if not author:
        print(f"No se encontró un autor para el post {instance.title}.")
        return

    # Notificación si el post se convierte en destacado
    if instance == post_destacado:
        subject = "¡Tu post es el Post Destacado! 🎉"
        message = f"Hola {author.username}, tu post '{instance.title}' ha sido seleccionado como el Post Destacado.¡Felicidades!"

        try:
            send_mail(
                subject,
                message,
                "groupmakex@gmail.com",
                [author.email],
                fail_silently=False,
            )
            print(
                f"Correo enviado al autor {author.username} notificando la pulicacion."
            )
        except Exception as e:
            print("Ocurrieron errores al notificar al autor del post: ", e)
            return

    # Notificación si el post está en el Top 5 de los más populares
    if instance in posts_populares:
        subject = "¡Tu post está en el Top 5 de los más populares! 🎉"
        message = f"Hola {author.username}, tu post '{instance.title}' está en el Top 5 de los posts más populares.¡Sigue así!"

        try:
            send_mail(
                subject,
                message,
                "groupmakex@gmail.com",
                [author.email],
                fail_silently=False,
            )
            print(
                f"Correo enviado al autor {author.username} notificando la pulicacion."
            )
        except Exception as e:
            print("Ocurrieron errores al notificar al autor del post: ", e)
            return
