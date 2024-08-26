from django.apps import AppConfig

class AuthorizationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'modulos.Authorization'

    def ready(self):
        import modulos.Authorization.roles  # Importa roles.py para registrar las señales y crear los grupos.
