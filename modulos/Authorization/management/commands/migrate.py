# app/management/commands/migrate.py

from django.core.management.base import no_translations
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor

from modulos.Authorization.permissions import _initialize_permissions
from modulos.Authorization.roles import _create_default_groups


# The code is from django/core/management/commands/migrate.py
def is_database_synchronized():
    connection = connections[DEFAULT_DB_ALIAS]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)


class Command(MigrateCommand):
    @no_translations
    def handle(self, *args, **options):
        print("-----------------------")
        print(" Corriendo migraciones ")
        print("-----------------------")
        super().handle(*args, **options)
        if is_database_synchronized():
            print("\n--------------------------------")
            print(" Inicializando permisos y roles ")
            print("--------------------------------")
            _initialize_permissions()
            _create_default_groups()
        else:
            print("No se pudieron inicializar los roles y permisos.")
            print("El estado de la BD es inconsistente. Por favor verifique los errores de migracion")
