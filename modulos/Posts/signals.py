from django.db.models.signals import pre_save
from django.dispatch import receiver

from modulos.Posts.models import Log, Post


@receiver(pre_save, sender=Post)
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
