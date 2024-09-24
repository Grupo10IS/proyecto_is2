# Cargar la configuración específica de producción si DJANGO_ENV está seteada a "production".
import os
from os import getenv

# Cargar configuraciones compartidas entre dev y producción
from .envs.common import *

print(f"DJANGO_ENV is: {os.getenv('DJANGO_ENV')}")

if getenv("DJANGO_ENV") == "production":
    from .envs.prod import *

    print("Modo Producción")
else:
    from .envs.dev import *

    print("Modo Desarrollo")
