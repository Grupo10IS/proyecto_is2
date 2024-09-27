from django.apps import AppConfig


class PostsConfig(AppConfig):
    """
    Configuración de la aplicación 'Posts'.

    Esta clase define la configuración predeterminada para la aplicación 'Posts',
    especificando el tipo de campo automático predeterminado para los modelos de la aplicación
    y el nombre del módulo de la aplicación.

    Attributes:
        default_auto_field (str): Tipo de campo automático predeterminado para los modelos de la aplicación.
        name (str): Nombre del módulo de la aplicación 'Posts'.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "modulos.Posts"

    def ready(self):
        import modulos.Posts.signals

