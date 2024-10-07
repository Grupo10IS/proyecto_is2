from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from modulos.Authorization.roles import SUBSCRIBER
from modulos.UserProfile.models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def add_to_default_group(sender, instance, created, **kwargs):
    """
    Señal para agregar un usuario al grupo predeterminado después de la creación.

    Esta función se conecta a la señal `post_save` del modelo `User` para añadir automáticamente
    el usuario recién creado al grupo predeterminado denominado 'SUBSCRIBER'.

    Nota:
        El grupo 'SUBSCRIBER' se crea si no existe ya.
    """
    if created:
        suscriptor_group, created = Group.objects.get_or_create(name=SUBSCRIBER)
        instance.groups.add(suscriptor_group)


# NOTIFICA AL USUARIO CUANDO SE REGISTRA A LA PLATAFORMA
@receiver(post_save, sender=UserProfile)
def notify_new_user(sender, instance, created, **kwargs):
    """
    Notifica al usuario con un correo de bienvenida cuando crea una cuenta nueva.
    """
    if created:
        print(f"Enviando correo de bienvenida a {instance.username} ({instance.email})")
        # Enviar correo de bienvenida
        subject = "¡Bienvenido a MakeX!"
        message = (
            f"Hola {instance.username},\n\n"
            f"Te damos la bienvenida a MakeX. Has sido asignado al rol de 'Suscriptor'.\n"
            "Disfruta de nuestra plataforma y explora el contenido disponible."
        )
        send_mail(
            subject,
            message,
            "groupmakex@gmail.com",
            [instance.email],
            fail_silently=False,
        )
        print(f"Correo de bienvenida enviado a {instance.username} ({instance.email})")


# Signal para detectar cambios en los roles del usuario
@receiver(m2m_changed, sender=UserProfile.groups.through)
def notify_user_role_change(sender, instance, action, pk_set, **kwargs):
    """
    Notifica al usuario cuando se le asigna o cambia un rol.
    """
    if action == "post_add":
        # Se han añadido roles nuevos
        new_roles = Group.objects.filter(pk__in=pk_set)

        for role in new_roles:
            print(
                f"Notificando al usuario {instance.username} sobre su nuevo rol: {role.name}"
            )
            subject = "Cambio en tu rol en MakeX"
            message = (
                f"Hola {instance.username},\n\n"
                f"Tu rol en MakeX ha cambiado. Ahora tienes el rol de '{role.name}'.\n"
                "Si tienes alguna duda, no dudes en contactarnos!"
            )
            try:
                send_mail(
                    subject,
                    message,
                    "groupmakex@gmail.com",
                    [instance.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(
                    f"No se pudo enviar el mail al usuario"
                )
