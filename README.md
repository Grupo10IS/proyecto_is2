
El sistema esta dockerizado y aqui las instrucciones
# Proyecto de Despliegue Automatizado

Este repositorio contiene un script para desplegar automáticamente versiones específicas de una aplicación dentro de un contenedor Docker utilizando `docker` y `docker-compose`.

## **Requisitos**

Antes de comenzar, asegúrate de tener instalados los siguientes programas en tu máquina:

- **Docker**: Puedes instalar Docker siguiendo las instrucciones oficiales [aquí](https://docs.docker.com/get-docker/).
- **Docker Compose**: Si estás utilizando una versión más reciente de Docker, Docker Compose ya viene incluido. De lo contrario, puedes instalarlo siguiendo las instrucciones oficiales [aquí](https://docs.docker.com/compose/install/).
**LUEGO SOLO TIENES QUE EJECUTAR**
  
  deploy_container con la siguiente sintaxis -> Uso: ```./deploy_container.sh [prod|dev]```

Antes verifica dar permiso de ejecucion -> ```chmod +x deploy_container.sh``` 🙇‍♂️
  
Verifica las instalaciones ejecutando los siguientes comandos:

```bash
docker --version
docker-compose --version

Para la administracion del sitio debera crear un nuevo usuario administrador, el cual sera
utilizando el comando:

```bash
python manage.py  new_admin
```

NOTA:
deberas contar con las siguientes variables de entorno en un archivo `.env` dentro de la raiz
del proyecto:

```bash
# stripe
export STRIPE_SECRET_KEY=stripe
export STRIPE_PUBLIC_KEY=stripe

# disqus
export DISQUS_API_KEY=disqus
export DISQUS_FORUM=disqus (default = 'makexfp-com')
```

Luego de estos pasos ya podra levantar el servidor con:

```bash
python manage.py  runserver
```

**TLDR**:

```bash
pip install -U poetry
poetry install
python manage.py migrate
python manage.py  new_admin
python manage.py  runserver
```

### Testing

Para correr la suit de test:

```bash
pytest
```

**[Documentacion automatizada](https://grupo10is.github.io/proyecto_is2/)**
