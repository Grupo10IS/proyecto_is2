import boto3
from botocore.exceptions import NoCredentialsError

from modulos.Authorization.permissions import (KANBAN_VIEW_PERMISSION,
                                               VIEW_PURCHASED_CATEGORIES)
from modulos.Categories.models import Category
from modulos.Posts.forms import SearchPostForm


def new_ctx(req, params):
    """
    Crea un diccionario de contexto de envoltura para renderizar plantillas, basado en los permisos
    del usuario y parámetros adicionales. Combina un contexto personalizado proporcionado como parámetro
    con el contexto común para el resto de las páginas y vistas.

    Argumentos:
        req (HttpRequest): El objeto de solicitud HTTP que contiene información del usuario.
        params (dict): Parámetros adicionales que se incluirán en el contexto.

    Retorna:
        dict: Un diccionario que contiene el contexto para renderizar plantillas, incluyendo permisos
        del usuario y una lista de categorías.

    Ejemplo:
        >>> base = {"form": NuestroFormulario, "data": NuestrosDatos}
        >>> ctx = new_ctx(request, base)
        >>> return render(req, "template", ctx)
    """
    sitios = []
    kanban_permission = False
    finances_permission = False
    payment_permission = False

    if req.user.is_authenticated:
        kanban_permission = req.user.has_perm(KANBAN_VIEW_PERMISSION)
        finances_permission = req.user.has_perm(VIEW_PURCHASED_CATEGORIES)

        # Para poder listar permisos "parecidos", en vez de tener que buscar por permisos especificos.
        # Esto ya que para ver el panel de control solo se necesita saber si se contiene
        # ciertos permisos, no permisos especificos. Da un asco terrible esto por cierto.
        permisos = req.user.get_all_permissions()
        for perm in permisos:
            if "user" in perm and perm not in sitios:
                sitios.append("user")
            if "post" in perm and perm not in sitios:
                sitios.append("post")
            if "categor" in perm and perm not in sitios:
                sitios.append("category")
            if "role" in perm and perm not in sitios:
                sitios.append("role")
            if "delete" in perm and perm not in sitios:
                sitios.append("delete")
            if "create" in perm and perm not in sitios:
                sitios.append("create")
            if "edit" in perm and perm not in sitios:
                sitios.append("edit")
            if "reports" in perm and perm not in sitios:
                sitios.append("reports")

    base = {
        "categories": Category.objects.all(),
        "permisos": sitios,
        "post_search_input": SearchPostForm,
        "has_kanban_access": kanban_permission,
        "has_financial_acces": finances_permission,
        "has_payment": payment_permission,
    }
    base.update(params)

    return base


def upload_to_aws_s3(file_path, bucket_name):
    """
    Sube un archivo a un bucket de Amazon S3 utilizando la API de boto3.

    Esta función permite cargar un archivo a un bucket de S3 especificado, con la opción de
    definir el nombre del objeto en S3. Si no se especifica el nombre del objeto, se utiliza
    el nombre del archivo como nombre del objeto en S3.

    Parámetros:
        - file_path (str): Ruta del archivo a subir. Este parámetro especifica la ubicación del
      archivo en el sistema local.
    - bucket_name (str): Nombre del bucket de S3 donde se subirá el archivo.
    - object_name (str, opcional): Nombre del objeto en S3. Si no se especifica, se utilizará
      el nombre del archivo.

    Retorna:
        - bool: Devuelve True si la carga fue exitosa.
    """
    print("Inicializando cliente S3...")
    s3 = boto3.client("s3")  # Simula la creación del cliente S3

    try:
        print(f"Subiendo {file_path} al bucket {bucket_name} en AWS S3...")

        # Simulación de la llamada a la función `upload_file`
        s3.upload_file(file_path, bucket_name, file_path.split("/")[-1])

        # Simula un mensaje de éxito
        print(f"Archivo '{file_path}' subido exitosamente a '{bucket_name}'.")

    except FileNotFoundError:
        print("Error: Archivo no encontrado.")
    except NoCredentialsError:
        print("Error: Credenciales no disponibles.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def download_from_aws(bucket_name, object_name, file_path):
    """
    Descarga un archivo desde un bucket de Amazon S3 utilizando la API de boto3.

    Esta función permite descargar un archivo desde un bucket de S3 especificado y guardarlo
    en el sistema de archivos local en la ubicación especificada por el usuario.

    Parámetros:
    - bucket_name (str): Nombre del bucket de S3 desde el cual se descargará el archivo.
    - object_name (str): Nombre del objeto en S3 que se desea descargar.
    - file_path (str): Ruta local donde se guardará el archivo descargado.

    Retorna:
    - bool: Devuelve True si la descarga fue exitosa, False en caso de error.
    """

    # Inicializa el cliente de S3
    s3 = boto3.client("s3")

    try:
        # Intento de descarga del archivo desde S3 al destino especificado
        s3.download_file(bucket_name, object_name, file_path)
        print(
            f"Archivo descargado exitosamente desde '{bucket_name}/{object_name}' a '{file_path}'"
        )
        return True

    except NoCredentialsError:
        # Manejo de excepción si faltan las credenciales de AWS
        print("Error: No se encontraron credenciales de AWS.")
        return False
    except Exception as e:
        # Captura cualquier otra excepción que pueda ocurrir
        print(f"Error inesperado: {str(e)}")
        return False
