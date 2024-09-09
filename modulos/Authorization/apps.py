from django.apps import AppConfig


class AuthorizationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modulos.Authorization"

    def ready(self):
        # Importar roles.py para registrar las señales
        import modulos.Authorization.roles
