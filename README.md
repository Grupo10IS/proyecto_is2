
1. [Desarrollo en ambiente local](#Para desarrollo en el ambiente local)
    * [Ejecucion](#ejecucion)
    * [Testing](#testing)
2. [Deploy automatizado con Docker](#Deploy Automatizado utilizando Docker)
    * [Requisitos Previos](#requisitos-previos)
    * [Ambiente de produccion y testing](#ambiente-de-produccion-y-testing)
    * [Acerca de `deploy_full.sh`](#acerca-de-`deploy_full.sh`)

**[Documentacion automatizada](https://grupo10is.github.io/proyecto_is2/)**

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


Si es la primera vez que se corre el proyecto, debera crear un nuevo administrador del sistema
con: 

```bash
python manage.py new_admin
```

### Testing

Para correr la suit de test:

```bash
pytest
```

# Deploy Automatizado utilizando Docker

Este repositorio contiene un script automatizado para desplegar la infraestructura necesaria
(en entornos de desarrollo o producción) y la aplicación Django basada en el repositorio
[`Grupo10IS/proyecto_is2`](https://github.com/Grupo10IS/proyecto_is2).

## Requisitos Previos

El proyecto proporciona un script que automatiza el proceso de levantar una imagen docker para
el ambiente de produccion y testing.

```bash
git clone https://github.com/Grupo10IS/proyecto_is2.git
cd proyecto_is2
bash ./deploy_full.sh
```

Antes de usar este script, asegúrate de cumplir con los siguientes requisitos:

- **Puerto 80**:
  libre para utilizar.
- **Docker**:
  Instalado en tu sistema.
  [Guía de instalación de Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**:
  Instalado en tu sistema.
  [Guía de instalación de Docker Compose](https://docs.docker.com/compose/install/)

## Acerca  de `deploy_full.sh`

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

## Como utilizar el script

El script primeramente requiere que ingrese el tipo de entorno que quiere inicializar:

```txt
1. Produccion
2. Testing
Ingrese el numero de la opcion: <su eleccion> 
```

Luego procedera a instanciar los contenedores docker.
Una vez terminado este proceso se le presentara una lista de los contenedores creados por
docker, ahora usted debe ingresar los nombres de los servidores. 

Por ejemplo, el script le mostrara lo siguiente:

```txt
Listando contenedores desplegados...
NAMES                   STATUS
1)      tmpgw5mfyd3z3-nginx-1   Up Less than a second
2)      tmpgw5mfyd3z3-web-1     Up Less than a second
3)      tmpgw5mfyd3z3-db-1      Up 1 second

Introduce el nombre del contenedor de la aplicación web: <web>
Introduce el nombre del contenedor de la base de datos: <db>
```

Usted debe ingresar el **NOMBRE** del contenedor que le corresponde.

En el caso del servidor de aplicacion web debe poner "tmpgw5mfyd3z3-web-1", y del contenedor de
la base de datos poner "tmpgw5mfyd3z3-db-1".

Tenga bien en cuenta de que los nombres seran *DISTINTOS* para usted, pero siempre contendran
lal terminacion de "web" o "db" o "nginx".

Finalmente el contenedor docker sera exitosamente instanciado.
Puede conectarse al servidor web desde el puerto ":80".

## Creacion del admin

Debera crear un nuevo administrador del sistema.
Esto lo hace conectandose al contenedor con:

```bash
docker exec -it csm-web bash
```

Luego puede correr el siguiente comando, el cual le pedira que ingrese los datos para el nuevo
admin: 

```bash
python manage.py new_admin
```
