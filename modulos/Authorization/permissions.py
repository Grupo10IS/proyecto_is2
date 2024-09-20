from os import _exit
from modulos.Pagos.models import Payment
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
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


# NOTE: esta funcion se utiliza en el comando migrate custom
def _initialize_permissions():
    """
    Inicializa y crea la lista de permisos disponibles dentro de la bd.

    Esta funcion es llamada dentro del comando custom "migrate" ubicado dentro del mismo modulo,
    el cual sobreescribe las funciones por defecto del comando migrate de django.
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

    print(f"- Permisos incializados correctamente")


def user_has_access_to_category(user, category):
    """
    Checks if the user has access to the given category.
    """
    # Verificar si la categoría es gratuita
    if category.tipo == category.GRATIS:
        return True

    # Verificar si el usuario tiene un pago exitoso para esta categoría
    if Payment.objects.filter(
        user=user, category=category, status="succeeded"
    ).exists():
        return True

    # Verificar si el usuario pertenece a grupos con acceso a la categoría
    from modulos.Authorization.roles import ADMIN, PUBLISHER, EDITOR, AUTOR, SUBSCRIBER

    if (
        category.tipo == category.SUSCRIPCION
        and user.groups.filter(
            name__in=[ADMIN, PUBLISHER, EDITOR, AUTOR, SUBSCRIBER]
        ).exists()
    ):
        return True

    if (
        category.tipo == category.PREMIUM
        and user.groups.filter(name__in=[ADMIN, PUBLISHER, EDITOR, AUTOR]).exists()
    ):
        return True

    return False
