from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from modulos.Authorization.roles import ADMIN
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
    Utilidad para pedir infoamcion de usuraio
    """
    username = input("Ingresa el nombre de usuario: ")
    email = input("Ingresa el correo electrónico: ")
    paswd = input("Ingresa la contrasena: ")
    pas_conf = input("Confirme su contrasena: ")

    return _credentials(username=username, email=email, paswd=paswd, pas_conf=pas_conf)


def create_admin(c: _credentials):
    """
    Genera un nuevo usuario administrado para el sistema. Este comando debe correrse
    para generar un nuevo usuario en el momento de realizar el despliegue.

    Raise (ValueError): cuando las credenciales del usuario no son validas.
    """

    # revision de credenciales
    if UserProfile.objects.filter(username=c.username).exists():
        raise ValueError(f'El usuario "{c.username}" ya existe.')

    # TODO: revision de contrasena, formato de email, formato de nombre de usuario

    user_profile = UserProfile.objects.create_user(
        username=c.username, email=c.email, password=c.paswd
    )

    admin_group = Group.objects.get(name=ADMIN)
    user_profile.groups.add(admin_group)

    user_profile.save()


class Command(BaseCommand):
    help = "Crear un nuevo UserProfile"

    def handle(self, *args, **kwargs):
        try:
            create_admin(_get_user_info())
            self.stdout.write(self.style.SUCCESS(f"Admin creado exitosamente."))
        except Exception as e:
            self.stdout.write(e.__str__())
