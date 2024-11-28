# Deploy Automatizado de Infraestructura y Aplicación Django

Este repositorio contiene un script automatizado para desplegar la infraestructura necesaria (en entornos de desarrollo o producción) y la aplicación Django basada en el repositorio [`Grupo10IS/proyecto_is2`](https://github.com/Grupo10IS/proyecto_is2).

## Requisitos Previos

Antes de usar este script, asegúrate de cumplir con los siguientes requisitos:

- **Docker**: Instalado en tu sistema. [Guía de instalación de Docker](https://docs.docker.com/get-docker/)
- **Docker Compose**: Instalado en tu sistema. [Guía de instalación de Docker Compose](https://docs.docker.com/compose/install/)

## Cómo Usar

### 1. Ejecutar el Script `deploy_full.sh`

El script `deploy_full.sh` se encarga de:

1. **Elegir el entorno a desplegar**:
   - **Producción (`prod`)**: Incluye Nginx y configuración optimizada para producción.
   - **Desarrollo (`dev`)**: Incluye configuración más sencilla, sin Nginx.

2. **Levantar la infraestructura con Docker Compose**:
   - Descarga y utiliza el repositorio correspondiente para el entorno seleccionado.

3. **Seleccionar la versión de la aplicación Django a desplegar**:
   - Lista los **tags disponibles** en el repositorio de la aplicación [`Grupo10IS/proyecto_is2`](https://github.com/Grupo10IS/proyecto_is2).
   - Despliega la versión del tag seleccionado.

4. **Reiniciar la base de datos (opcional)**:
   - Limpia y reinicia la base de datos para aplicar las migraciones sin errores.

5. **Aplicar migraciones y archivos estáticos automáticamente**:
   - Configura el entorno Django para estar listo para usar.

### 2. Ejecución

Sigue estos pasos:

1. Clona este repositorio:
   ```bash
   git clone https://github.com/Grupo10IS/proyecto_is2.git
   cd DeployAbsolutCSM


```
### Testing

Para correr la suit de test:

```bash
pytest
```

**[Documentacion automatizada](https://grupo10is.github.io/proyecto_is2/)**
