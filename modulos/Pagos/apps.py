from django.apps import AppConfig

class PagosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modulos.Pagos"

    def ready(self):
        import modulos.Pagos.signals
