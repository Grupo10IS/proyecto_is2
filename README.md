# First run

Para levantar le proyecto se necesitan las siguientes dependencias:

- Pytohon 3.12 + pip
- Postgres SQL 16.3

Para la instalacion de las dependencias necesitara instalar `poetry`, para hacerlo se
recomienda crear y activar un `virtualenv` en python y correr:

```bash
pip install -U poetry
```

Luego de ello poetry instalara todas las dependencias de manera automatica utilizando:

```bash
poetry install
```

Una vez instaladas las dependencias debera de configurar su base de datos y crear una nueva DB
llamada `proyecto`.
Luego de ello asegurese de estar corriendo el cliente de postgres.

Posteriormente realize las migraciones necesarias con el comando:

```bash
python manage.py migrate
```

Esto inicializara la base de datos e inicializara el sistema de roles y permisos de forma
automatica.

Para la administracion del sition debera crear un nuevo usuario administrador, el cual sera
utilizando el comando:

```bash
python manage.py  new_admin
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
