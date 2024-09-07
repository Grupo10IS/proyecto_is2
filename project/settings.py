from os import getenv

# Cargar configuraciones compartidas entre dev y produccion
from .envs.common import *

# Cargar la configuracion especifica de produccion si es que la variable de entorno
# PRODUCTION_DEPLOY esta seteada a true.

if getenv("PRODUCTION_DEPLOY") == "true":
    from .envs.prod import *
else:
    from .envs.dev import *
