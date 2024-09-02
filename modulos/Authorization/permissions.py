from os import _exit

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from modulos.UserProfile.models import UserProfile

#####
# Definicion de permisos
#####

# usuarios
USERS_VIEW_ALL_PROFILES_PERMISSION = "users_view_all_profiles_permission"

# posts
POST_CREATE_PERMISSION = "post_creation_permission"
POST_EDIT_PERMISSION = "post_edit_permission"
POST_DELETE_PERMISSION = "post_delete_permission"
POST_POST_PERMISSION = "post_post_permission"
POST_POST_PERMISSION = "post_post_permission"
POST_DECLINE_PERMISSION = "post_decline_permission"

# roles
ROLE_VIEW_PERMISSION = "role_view_permission"
ROLE_MANAGE_PERMISSION = "role_manage_permission"

# categoria
CATEGORY_MANAGE_PERMISSION = "category_manage_permission"

# NOTE: se utiliza para listar los permisos en la vista
permissions = [
    # usuarios
    (USERS_VIEW_ALL_PROFILES_PERMISSION, "Ver todos los perfiles de usuarios"),
    # posts
    (POST_CREATE_PERMISSION, "Permiso para crear publicaciones"),
    (POST_EDIT_PERMISSION, "Permiso para editar publicaciones"),
    (POST_DELETE_PERMISSION, "Permiso para eliminar publicaciones"),
    (POST_POST_PERMISSION, "Permiso para publicar publicaciones"),
    (POST_DECLINE_PERMISSION, "Permiso para rechazar publicaciones"),
    # roles
    (ROLE_VIEW_PERMISSION, "Permiso para listar los roles del sistema"),
    (ROLE_MANAGE_PERMISSION, "Permiso para crear y eliminar los roles del sistema"),
    # categoria
    (CATEGORY_MANAGE_PERMISSION, "Permiso para gestionar categorías"),
]

#####
# Creacion de permisos
#####


@receiver(post_migrate)
def initialize_permissions(sender, **kwargs):
    """
    Inicializa y crea la lista de permisos disponibles dentro de la bd luego de
    crear las migraciones.

    Esta senhal se lanza automaticamente luego de realizar las migraciones 
    con el comendo manage.py migrate.
    """
    for perm in permissions:
        try:
            Permission.objects.update_or_create(
                codename=perm[0],
                name=perm[1],
                content_type=ContentType.objects.get_for_model(UserProfile),
            )
        except Exception as e:
            print(e)
            _exit(1)

    print(f"Default permisos incializados")
