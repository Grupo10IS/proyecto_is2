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
    Evitar la eliminacion de los roles por defecto del sistema
    """
    if instance.name in default_roles:
        raise PermissionDenied("Este rol no puede ser eliminado.")


# NOTE: si da problemas con el orden de los permisos, entonces mover esto
# al final del archivo de initialize_permissions
@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Crear los roles por defecto despues de realizar migraciones
    """
    for role_name, permissions in default_roles.items():
        role, _ = Group.objects.get_or_create(name=role_name)

        # Limpiar permisos existentes
        role.permissions.clear()

        # Anadir los permisos pertinentes
        for perm in permissions:
            permission = Permission.objects.get(codename=perm)
            role.permissions.add(permission)

        role.save()

    print(f"Created default roles")
