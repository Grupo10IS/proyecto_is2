"""
Genera un nuevo usuario administrado para el sistema. Este comando debe correrse
para generar un nuevo usuario en el momento de realizar el despliegue.
"""

import re

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from modulos.Authorization.roles import ADMIN, EDITOR, PUBLISHER
from modulos.UserProfile.models import UserProfile

# NOTE: para propositos de testing esta estructurado de esa manera


class _credentials:
    username: str
    email: str
    paswd: str
    pas_conf: str

    def __init__(self, username: str, email: str, paswd: str, pas_conf: str):
        self.username = username
        self.email = email
        self.paswd = paswd
        self.pas_conf = pas_conf


def _get_user_info() -> _credentials:
    """
    Utilidad para pedir informacion de usuario desde la terminal
    """
    username = input("Ingresa el nombre de usuario: ").strip()
    email = input("Ingresa el correo electrónico: ").strip()
    paswd = input("Ingresa la contrasena: ").strip()
    pas_conf = input("Confirme su contrasena: ").strip()

    return _credentials(username=username, email=email, paswd=paswd, pas_conf=pas_conf)


def has_valid_credentials(c: _credentials) -> tuple[bool, str]:
    """
    Utilidad para la comprobacion de credenciales del usuario. Retorna true si las
    credenciales son validas. En caso de no serlo retorna false y un mensaje de error.
    """

    # revisar que el usuario solo contenga letras, numeros y _ en su nombre
    if not bool(re.match(r"^[\w]+$", c.username)):
        return False, "Username can only have letters, numbers and _"

    if c.pas_conf != c.paswd:
        return False, "Passwords are not equal"

    # que el email sea valido
    patron = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(patron, c.email) is not None:
        return False, "Invalid email format"

    return True, ""


def create_admin(c: _credentials):
    # revision de credenciales
    valid, msg = has_valid_credentials(c)
    if not valid:
        raise ValueError(f"Error: {msg}")

    # Creacion de usuario
    if not has_valid_credentials(c):
        raise ValueError(f'El usuario "{c.username}" ya existe.')

    if UserProfile.objects.filter(username=c.username).exists():
        raise ValueError(f'El usuario "{c.username}" ya existe.')

    user_profile = UserProfile.objects.create_user(
        username=c.username, email=c.email, password=c.paswd
    )

    # asign groups
    admin_group = Group.objects.get(name=ADMIN)
    editor_group = Group.objects.get(name=EDITOR)
    publisher_group = Group.objects.get(name=PUBLISHER)

    user_profile.groups.add(admin_group)
    user_profile.groups.add(publisher_group)
    user_profile.groups.add(editor_group)

    user_profile.save()


class Command(BaseCommand):
    help = "Crear un nuevo UserProfile"

    def handle(self, *args, **kwargs):
        try:
            create_admin(_get_user_info())
            self.stdout.write(self.style.SUCCESS(f"Admin creado exitosamente."))
        except Exception as e:
            self.stdout.write(e.__str__())
