# Cargar la configuración específica de producción si DJANGO_ENV está seteada a "production".
from os import getenv

# Cargar configuraciones compartidas entre dev y producción
from .envs.common import *

if getenv("DJANGO_ENV") == "production":
    print(f"DJANGO_ENV: Produccion")
    from .envs.prod import *
else:
    print(f"DJANGO_ENV: Development")
    from .envs.dev import *
