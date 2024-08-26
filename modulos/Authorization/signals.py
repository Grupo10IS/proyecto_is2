from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from modulos.Authorization.roles import *


@receiver(pre_delete, sender=Group)
def prevent_default_role_deletion(sender, instance, **kwargs):
    default_roles = [ADMIN]

    if instance.name in default_roles:
        raise PermissionDenied("Este rol no puede ser eliminado.")

