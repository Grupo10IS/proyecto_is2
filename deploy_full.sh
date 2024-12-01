#!/bin/bash
# Función para verificar si usar docker-compose o docker compose
function get_compose_command {
    if command -v docker-compose &> /dev/null; then
        echo "docker-compose"
    elif docker compose version &> /dev/null; then
        echo "docker compose"
    else
        echo "Error: Ni docker-compose ni docker compose están instalados."
        exit 1
    fi
}

COMPOSE_COMMAND=$(get_compose_command)

# Limpiar contenedores y volúmenes existentes
echo "Deteniendo y eliminando contenedores existentes..."
docker ps -aq | xargs -r docker stop
docker ps -aq | xargs -r docker rm
docker volume ls -q | xargs -r docker volume rm

# Elegir entorno a desplegar
echo "Elige el entorno para desplegar:"
echo "1. Producción"
echo "2. Desarrollo"
read -p "Introduce el número de la opción: " ENV_CHOICE

if [ "$ENV_CHOICE" == "1" ]; then
    REPO_ENTORNO="https://github.com/JuanchoGonza98/DeployAbsolutCSM.git"
    echo "Entorno seleccionado: Producción"
elif [ "$ENV_CHOICE" == "2" ]; then
    REPO_ENTORNO="https://github.com/JuanchoGonza98/DeployingCMSDjango.git"
    echo "Entorno seleccionado: Desarrollo"
else
    echo "Error: Opción inválida."
    exit 1
fi

# Clonar el repositorio de infraestructura
TMP_DIR_INFRA=$(mktemp -d)
echo "Clonando el repositorio de infraestructura $REPO_ENTORNO..."
git clone "$REPO_ENTORNO" "$TMP_DIR_INFRA"

if [ $? -ne 0 ]; then
    echo "Error: No se pudo clonar el repositorio de infraestructura."
    rm -rf "$TMP_DIR_INFRA"
    exit 1
fi

cd "$TMP_DIR_INFRA" || exit

# Desplegar infraestructura con Docker Compose
if [ -f "docker-compose.yml" ]; then
    echo "Desplegando la infraestructura con Docker Compose..."
    docker compose up -d
    if [ $? -ne 0 ]; then
        echo "Error: No se pudo desplegar la infraestructura."
        rm -rf "$TMP_DIR_INFRA"
        exit 1
    fi
else
    echo "Error: No se encontró un archivo docker-compose.yml en el repositorio."
    rm -rf "$TMP_DIR_INFRA"
    exit 1
fi

# Paso 3: Identificar contenedores
echo "Listando contenedores desplegados..."
docker ps -a --format "table {{.Names}}\t{{.Status}}" | awk '{if(NR==1){print $0}else{print NR-1 ")\t" $0}}'
read -p "Introduce el nombre del contenedor de la aplicación web: " CONTAINER_WEB
read -p "Introduce el nombre del contenedor de la base de datos: " CONTAINER_DB

# Paso 4: Limpiar base de datos
echo "Limpiando la base de datos en el contenedor $CONTAINER_DB..."
docker exec -i "$CONTAINER_DB" psql -U postgres -d proyecto -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
if [[ $? -ne 0 ]]; then
    echo "Error al limpiar la base de datos. Asegúrate de que el contenedor $CONTAINER_DB está configurado correctamente."
    exit 1
fi
echo "Base de datos limpiada con éxito."

# Paso 5: Clonar el proyecto principal y listar tags
REPO_PROYECTO="https://github.com/Grupo10IS/proyecto_is2.git"
echo "Clonando el repositorio principal para listar los tags..."
TMP_DIR_PROYECTO=$(mktemp -d)
git clone --bare "$REPO_PROYECTO" "$TMP_DIR_PROYECTO/repo"

if [ $? -ne 0 ]; then
    echo "Error: No se pudo clonar el repositorio principal."
    rm -rf "$TMP_DIR_PROYECTO"
    exit 1
fi

echo "Tags disponibles en el repositorio:"
git --git-dir="$TMP_DIR_PROYECTO/repo" tag

read -p "Introduce el NOMBRE del tag que quiere desplegar: " TAG

# Paso 6: Clonar el tag dentro del contenedor web
docker exec -it "$CONTAINER_WEB" /bin/bash -c "
    apt-get update &&
    apt-get install -y git &&
    mkdir -p /app/temp_deploy &&
    cd /app/temp_deploy &&
    git clone $REPO_PROYECTO proyecto_temp &&
    cd proyecto_temp &&
    git checkout tags/$TAG &&
    cp -r . /app &&
    cd /app &&
    rm -rf /app/temp_deploy &&
    sed -i 's/localhost/db/g' /app/project/envs/common.py &&
    poetry install --only main --no-interaction &&
    poetry run python manage.py migrate &&
    poetry run python manage.py collectstatic --noinput
"

if [ $? -ne 0 ]; then
    echo "Error: Falló el despliegue del tag dentro del contenedor."
    exit 1
fi

echo "¡Despliegue completado para el entorno '$ENTORNO' con el tag '$TAG'!"
