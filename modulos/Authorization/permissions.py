from os import _exit

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from modulos.UserProfile.models import UserProfile

POST_EDIT_PERMISSION = "post_edit_permission"

#####
# Definicion de permisos
#####

# modificacion de usuarios
USERS_VIEW_ALL_PROFILES_PERMISSION = "users_view_all_profiles_permission"

# posts
POST_CREATE_PERMISSION = "post_creation_permission"
POST_EDIT_PERMISSION = "post_edit_permission"
POST_DELETE_PERMISSION = "post_delete_permission"

#####
# Creacion de permisos
#####


@receiver(post_migrate)
def initialize_permissions(sender, **kwargs):
    """
    Inicializa y crea la lista de permisos disponibles dentro de la bd luego de
    crear las migraciones
    """
    permissions = [
        # usuarios
        (USERS_VIEW_ALL_PROFILES_PERMISSION, "Ver todos los perfiles de usuarios"),

        # posts
        (POST_CREATE_PERMISSION, "Permiso para crear publicaciones"),
        (POST_EDIT_PERMISSION, "Permiso para editar publicaciones"),
        (POST_DELETE_PERMISSION, "Permiso para eliminar publicaciones"),
    ]

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
