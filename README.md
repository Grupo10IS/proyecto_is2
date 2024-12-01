**[Documentacion automatizada](https://grupo10is.github.io/proyecto_is2/)**

# Deploy Automatizado utilizando Docker

Este repositorio contiene un script automatizado para desplegar la infraestructura necesaria
(en entornos de desarrollo o producción) y la aplicación Django basada en el repositorio
[`Grupo10IS/proyecto_is2`](https://github.com/Grupo10IS/proyecto_is2).

## Requisitos Previos

Antes de usar este script, asegúrate de cumplir con los siguientes requisitos:

- **Docker**:
  Instalado en tu sistema.
  [Guía de instalación de Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**:
  Instalado en tu sistema.
  [Guía de instalación de Docker Compose](https://docs.docker.com/compose/install/)

## Ambiente de produccion y testing

  El proyecto proporciona un script que automatiza el proceso de levantar una imagen docker
  para el ambiente de produccion y testing.

```bash
git clone https://github.com/Grupo10IS/proyecto_is2.git
cd proyecto_is2
bash ./deploy_full.sh
```

### Acerca  de `deploy_full.sh`

El script realiza las siguiente tareas de manera automatica y sin necesidad de intervencion:

1. **Elegir el entorno a desplegar**:
   - **Producción (`prod`)**:
     Incluye Nginx y configuración optimizada para producción.
   - **Desarrollo (`dev`)**:
     Incluye configuración más sencilla, sin Nginx.

2. **Levantar la infraestructura con Docker Compose**:
   - Descarga y utiliza el repositorio correspondiente para el entorno seleccionado.

3. **Seleccionar la versión de la aplicación Django a desplegar**:
   - Lista los **tags disponibles** en el repositorio de la aplicación
     [`Grupo10IS/proyecto_is2`](https://github.com/Grupo10IS/proyecto_is2).
   - Despliega la versión del tag seleccionado.

4. **Reiniciar la base de datos (opcional)**:
   - Limpia y reinicia la base de datos para aplicar las migraciones sin errores.

5. **Aplicar migraciones y archivos estáticos automáticamente**:
   - Configura el entorno Django para estar listo para usar.
  
# Para desarrollo en el ambiente local

Clona el repositorio con el siguiente comando:
```bash
git clone https://github.com/Grupo10IS/proyecto_is2.git 
cd proyecto_is2
```

Se debe tener instalado `python`, `poetry` y `postgres` (con una nueva DB llamada `proyecto`).

Luego debes crear colocar un archivo `.env` dentro de este directorio, el cual contendra las
variables de entorno necesarias.

```bash
STRIPE_SECRET_KEY=xxxxxxxxxxxxxxxx
STRIPE_PUBLIC_KEY=xxxxxxxxxxxxxxxx
DISQUS_API_KEY=xxxxxxxxxxxxxxxx
```

Luego se requiere de la instalacion de las dependencias con poetry:

```bash
poetry install
```

### Ejecucion

Para ejecutar el proyecto simplemente:
```bash
python manage.py runserver
```

### Testing

Para correr la suit de test:

```bash
pytest
```
