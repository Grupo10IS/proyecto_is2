from os import _exit

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from modulos.UserProfile.models import UserProfile

POST_CREATE_PERMISSION = "post_creation_permission"
POST_EDIT_PERMISSION = "post_edit_permission"
POST_DELETE_PERMISSION = "post_delete_permission"


def initialize_permissions():
    permissions = [
        (POST_CREATE_PERMISSION, "Permiso para crear publicaciones"),
        (POST_EDIT_PERMISSION, "Permiso para editar publicaciones"),
        (POST_DELETE_PERMISSION, "Permiso para eliminar publicaciones"),
        # NOTE: agregar mas permisos aca
    ]

    for perm in permissions:
        try:
            Permission.objects.update_or_create(
                codename=perm[0],
                name=perm[1],
                content_type=ContentType.objects.get_for_model(UserProfile),
            )
            print(f"Permiso creado: {perm[0]}")
        except Exception as e:
            print(e)
            _exit(1)
