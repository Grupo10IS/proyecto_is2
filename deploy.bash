# Requerimientos antes de correr el script:
# - python3,
# - pip,
# - nginx (para produccion)
# - gunicorn (para produccion).
# - postgres
#
# Tener tambien configuradas las variables de entorno necesarias para el proyecto
# Y la configuracion de nginx con gunicorn.

tag=$1
prod=$2

# reclonar el repo
# cambiar a la rama
git pull
if [[ -n $tag ]]; then
    git checkout $tag
fi

# instalar dependencias
pip install poetry

# inciar ambiente virtual
poetry env use
poetry install

python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

if [[ -n $prod ]]; then
    systemctl restart gunicorn
    systemctl runserver
fi
