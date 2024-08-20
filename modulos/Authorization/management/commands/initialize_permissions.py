from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from modulos.Authorization import roles
from modulos.Authorization.permissions import *


class Command(BaseCommand):
    help = "Incializar los roles y permisos del sistema"

    def handle(self, *args, **kwargs):
        initialize_permissions()
        print()

        # Definir los roles por defecto y sus permisos
        roles_permissions = {
            roles.ADMIN: [POST_CREATE_PERMISSION],
        }

        # Crear o actualizar los roles por defecto
        for role_name, permissions in roles_permissions.items():
            role, created = Group.objects.get_or_create(name=role_name)
            if created:
                self.stdout.write(f"Created role: {role_name}")
            else:
                self.stdout.write(f"Updated role: {role_name}")

            # Limpiar permisos existentes
            role.permissions.clear()

            # Anadir los permisos pertinentes
            for codename in permissions:
                permission = Permission.objects.get(codename=codename)
                role.permissions.add(permission)

        self.stdout.write("Roles y permisos creados exitosamente")
