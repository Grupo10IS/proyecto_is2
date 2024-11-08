# Este script automatiza la configuración de un entorno de Django, incluyendo 
# la instalación de dependencias, la configuración de la base de datos, y la 
# opción de iniciar el servidor en modo producción o desarrollo.

# Pre-requisitos para ejecutar este script:
# - Python 3
# - pip (administrador de paquetes para Python)
# - nginx (solo para modo producción)
# - gunicorn (solo para modo producción)
# - PostgreSQL configurado y con permisos para el usuario 'postgres'

# Pasos previos:
# - Configurar las variables de entorno necesarias para el proyecto
# - Configurar nginx con gunicorn si se desea ejecutar en modo producción

# Uso:
# ./script.sh [tag] [prod] [admin]
#   tag: (opcional) Nombre de la etiqueta o rama de git que se desea utilizar
#   prod: (opcional) Indica que el entorno es de producción (usa nginx y gunicorn)
#   admin: (opcional) Crea un usuario administrador para la aplicación

# Ejemplo:
# ./script.sh v1.0 prod admin

tag=$1  # etiqueta o rama de git
prod=$2  # indica si se ejecuta en producción
admin=$3  # indica si se crea un usuario administrador

# 1. Actualizar el repositorio y cambiar a la rama o etiqueta especificada
git pull
if [[ -n $tag ]]; then
    git checkout $tag -f
fi

# 2. Iniciar PostgreSQL y crear la base de datos para el proyecto
systemctl start postgres
createdb -U postgres proyecto

# 3. Instalar dependencias del proyecto usando Poetry
pip install poetry

# 4. Configurar e instalar el ambiente virtual
poetry env use
poetry install

# 5. Aplicar migraciones y recolectar archivos estáticos
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# 6. (Opcional) Crear un usuario administrador si se especifica 'admin'
if [[ -n $admin ]]; then
    python manage.py new_admin
fi

# 7. Ejecutar el servidor en modo producción o desarrollo
if [[ -n $prod ]]; then
    # Modo producción: reiniciar gunicorn y ejecutar con nginx
    systemctl restart gunicorn
    systemctl restart nginx
else
    # Modo desarrollo: iniciar el servidor de desarrollo de Django
    python manage.py runserver
fi
