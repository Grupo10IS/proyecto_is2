#!/bin/bash

# Validar que se haya ingresado un parámetro
if [ $# -ne 1 ]; then
    echo "Uso: $0 [prod|dev]"
    exit 1
fi

# Variable para el repositorio
REPO=""
BRANCH="main"  # Por defecto, se usa la rama main

# Definir el repositorio según el parámetro
if [ "$1" == "prod" ]; then
    REPO="https://github.com/JuanchoGonza98/DeployAbsolutCSM.git"
elif [ "$1" == "dev" ]; then
    REPO="https://github.com/JuanchoGonza98/DeployingCMSDjango.git"
else
    echo "Error: El parámetro debe ser 'prod' o 'dev'."
    exit 1
fi

# Crear un directorio temporal para clonar el repositorio
TMP_DIR=$(mktemp -d)

# Verificar si la creación del directorio temporal fue exitosa
if [ ! -d "$TMP_DIR" ]; then
    echo "Error: No se pudo crear un directorio temporal."
    exit 1
fi

# Clonar el repositorio en el directorio temporal
echo "Clonando el repositorio $REPO..."
git clone --branch "$BRANCH" "$REPO" "$TMP_DIR"

# Verificar si el clon fue exitoso
if [ $? -ne 0 ]; then
    echo "Error: No se pudo clonar el repositorio."
    rm -rf "$TMP_DIR"
    exit 1
fi

# Cambiar al directorio del repositorio
cd "$TMP_DIR" || exit

# Ejecutar docker-compose
if [ -f "docker-compose.yml" ]; then
    echo "Ejecutando docker-compose up -d..."
    docker-compose up -d
    if [ $? -ne 0 ]; then
        echo "Error: No se pudo ejecutar docker-compose."
        rm -rf "$TMP_DIR"
        exit 1
    fi
else
    echo "Error: No se encontró un archivo docker-compose.yml en el repositorio."
    rm -rf "$TMP_DIR"
    exit 1
fi

# Limpiar el directorio temporal
rm -rf "$TMP_DIR"

echo "¡Todo listo! La aplicación se está ejecutando."
