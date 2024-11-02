from django.contrib.auth.models import Group, Permission
from django.core.exceptions import PermissionDenied
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from modulos.Authorization.permissions import *

ADMIN = "Administrador"
PUBLISHER = "Publicador"
EDITOR = "Editor"
AUTOR = "Autor"
SUBSCRIBER = "Suscriptor"
FINANCIAL = "Financiero"

# Roles por defecto y sus permisos
default_roles = {
    ADMIN: [
        USERS_VIEW_ALL_PROFILES_PERMISSION,
        ROLE_VIEW_PERMISSION,
        ROLE_MANAGE_PERMISSION,
        POST_DELETE_PERMISSION,
        CATEGORY_MANAGE_PERMISSION,
        VIEW_REPORTS,
        POST_REVIEW_PERMISSION,
        KANBAN_VIEW_PERMISSION,
        VIEW_PURCHASED_CATEGORIES,
        POST_HIGHLIGHT_PERMISSION,
    ],
    SUBSCRIBER: [PAYMENT_PERMISSION],
    AUTOR: [POST_CREATE_PERMISSION, KANBAN_VIEW_PERMISSION],
    EDITOR: [
        POST_EDIT_PERMISSION,
        POST_REVIEW_PERMISSION,
        KANBAN_VIEW_PERMISSION,
        POST_APPROVE_PERMISSION,
    ],
    PUBLISHER: [
        POST_POST_PERMISSION,
        POST_REVIEW_PERMISSION,
        POST_REJECT_PERMISSION,
        KANBAN_VIEW_PERMISSION,
        POST_PUBLISH_PERMISSION,
    ],
    FINANCIAL: [VIEW_PURCHASED_CATEGORIES],
}


@receiver(pre_delete, sender=Group)
def prevent_default_role_deletion(sender, instance, **kwargs):
    """
    Evitar la eliminacion de los roles por defecto del sistema
    """
    if instance.name in default_roles:
        raise PermissionDenied("Este rol no puede ser eliminado.")


# NOTE: esta funcion se utiliza en el comando migrate custom
def create_default_groups():
    """
    Crear los roles por defecto configurados en el sistema

    Esta funcion es llamada dentro del comando custom "migrate" ubicado dentro del mismo modulo,
    el cual sobreescribe las funciones por defecto del comando migrate de django.
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

    print(f"- Roles por defecto inicializados correctamente")
