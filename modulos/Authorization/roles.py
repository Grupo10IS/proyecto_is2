from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db.models.signals import post_migrate, pre_delete
from django.dispatch import receiver

from modulos.Authorization.permissions import *

ADMIN = "admin"
PUBLISHER = "publicador"
EDITOR = "editor"
AUTOR = "publicador"
SUBSCRIBER = "suscriptor"

# Roles por defecto y sus permisos
default_roles = {ADMIN: [USERS_VIEW_ALL_PROFILES_PERMISSION], SUBSCRIBER: []}


@receiver(pre_delete, sender=Group)
def prevent_default_role_deletion(sender, instance, **kwargs):
    """
    Evitar la eliminacino de los roles por defecto del sistema
    """
    if instance.name in default_roles:
        raise PermissionDenied("Este rol no puede ser eliminado.")


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Crear los roles por defecto despues de realizar migraciones
    """
    for group_name in default_roles:
        Group.objects.get_or_create(name=group_name)

        # Crear o actualizar los roles por defecto
        for role_name, permissions in default_roles.items():
            role, created = Group.objects.get_or_create(name=role_name)

            # Limpiar permisos existentes
            role.permissions.clear()

            # Anadir los permisos pertinentes
            for codename in permissions:
                permission = Permission.objects.get(codename=codename)
                role.permissions.add(permission)

    print(f"Created default roles")
