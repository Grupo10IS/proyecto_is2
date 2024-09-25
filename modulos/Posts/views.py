from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http.response import HttpResponseBadRequest
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (POST_CREATE_PERMISSION,
                                               POST_DELETE_PERMISSION,
                                               POST_EDIT_PERMISSION)
from modulos.Authorization.roles import ADMIN
from modulos.Categories.models import Category
from modulos.Posts.buscador import buscador
from modulos.Posts.forms import NewPostForm, SearchPostForm
from modulos.Posts.models import Post
from modulos.utils import new_ctx


def home_view(req):
    """
    Vista de inicio 'home_view'.

    Esta vista verifica si el usuario está autenticado y obtiene los 10 últimos posts.
    Se utiliza la plantilla 'pages/home.html' para mostrar la información al usuario.

    Args:
        req (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/home.html'.
    """
    ctx = new_ctx(req, {"posts": Post.objects.all()[:10]})
    return render(req, "pages/home.html", context=ctx)


def view_post(request, id):
    """
    Vista de detalle de publicación 'PostDetailView'.

    Esta vista muestra los detalles de un solo objeto 'Post'.
    Utiliza el modelo 'Post' para recuperar la instancia específica y renderiza el contenido
    utilizando la plantilla 'posts/post_detail.html'.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a mostrar.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'posts/post_detail.html'.
    """
    post = get_object_or_404(Post, id=id)  # Obtiene el post o devuelve un error 404
    tags = (
        post.tags.split(",") if post.tags else []
    )  # Divide las etiquetas en una lista
    tags = [tag.strip() for tag in tags]  # Elimina espacios en blanco

    es_favorito = post.favorites.filter(
        id=request.user.id
    ).exists()  # Verifica si el post es favorito del usuario actual
    ctx = new_ctx(
        request,
        {
            "post": post,
            "tags": tags,
            "categories": Category.objects.all(),
            "es_favorito": es_favorito,
        },
    )
    return render(request, "pages/post_detail.html", context=ctx)


@login_required
@permissions_required([POST_CREATE_PERMISSION])
def create_post(request):
    """
    Vista para crear un nuevo post.

    Esta vista maneja tanto la visualización del formulario como el procesamiento del
    mismo al enviar los datos. Si el formulario es válido, se crea el post.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Redirección a la vista del post creado o renderización del formulario con errores.
    """
    if request.method == "POST":
        post = NewPostForm(
            request.POST, request.FILES
        )  # Inicializa el formulario con los datos enviados
        if not post.is_valid():  # Verifica la validez del formulario
            return HttpResponseBadRequest("Datos proporcionados invalidos")

        p = post.save(
            commit=False
        )  # Guarda el post sin hacer commit a la base de datos
        p.author = request.user  # Asigna el autor al post
        p.save()  # Guarda el post en la base de datos
        return redirect("/posts/" + str(p.id))  # Redirige a la vista del post creado

    ctx = new_ctx(request, {"form": NewPostForm})  # Crea el contexto con el formulario
    return render(request, "pages/new_post.html", context=ctx)


@login_required
@permissions_required(
    [POST_CREATE_PERMISSION, POST_EDIT_PERMISSION, POST_DELETE_PERMISSION]
)
def manage_post(request):
    """
    Vista para gestionar los posts.

    Esta vista lista todos los posts del usuario actual o de todos los usuarios
    si el usuario pertenece al grupo 'Administrador'.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/post_list.html'.
    """
    is_admin = Group.objects.filter(
        name=ADMIN, user=request.user
    ).exists()  # Verifica si el usuario es administrador
    posts = (
        Post.objects.all() if is_admin else Post.objects.filter(author=request.user)
    )  # Obtiene los posts correspondientes

    permisos = (
        request.user.get_all_permissions()
    )  # Obtiene todos los permisos del usuario

    # Definición de permisos en variables booleanas
    perm_create = "UserProfile." + POST_CREATE_PERMISSION in permisos
    perm_edit = "UserProfile." + POST_EDIT_PERMISSION in permisos
    perm_delete = "UserProfile." + POST_DELETE_PERMISSION in permisos

    # Definición de contexto basado en permisos
    ctx = new_ctx(
        request,
        {
            "posts": posts,
            "perm_create": perm_create,
            "perm_edit": perm_edit,
            "perm_delete": perm_delete,
        },
    )
    return render(request, "pages/post_list.html", ctx)


@login_required
@permissions_required([POST_DELETE_PERMISSION])
def delete_post(request, id):
    """
    Vista para eliminar un post.

    Esta vista muestra un mensaje de confirmación antes de eliminar un post.
    Si la solicitud es un POST, se elimina el post y se redirige a la lista de posts.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a eliminar.

    Returns:
        HttpResponse: Redirección a la lista de posts o renderización de la confirmación de eliminación.
    """
    post = get_object_or_404(Post, pk=id)  # Obtiene el post o devuelve un error 404

    if request.method == "POST":
        post.delete()  # Elimina el post
        return redirect("post_list")  # Redirige a la lista de posts

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})  # Crea el contexto con el post a eliminar
    return render(request, "pages/post_confirm_delete.html", ctx)


@login_required
@permissions_required([POST_EDIT_PERMISSION, POST_CREATE_PERMISSION])
def edit_post(request, id):
    """
    Vista para editar un post existente.

    Esta vista carga el formulario con los datos del post y procesa la actualización
    si se envían nuevos datos.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a editar.

    Returns:
        HttpResponse: Redirección a la lista de posts o renderización del formulario con los datos del post.
    """
    post = get_object_or_404(Post, pk=id)  # Obtiene el post o devuelve un error 404
    if request.method == "POST":
        form = NewPostForm(
            request.POST, request.FILES, instance=post
        )  # Inicializa el formulario con el post existente
        if form.is_valid():  # Verifica la validez del formulario
            form.save()  # Guarda los cambios en el post
            return redirect("post_list")  # Redirige a la lista de posts

    form = NewPostForm(
        instance=post
    )  # Si no es un POST, muestra el formulario con los datos del post
    return render(request, "pages/new_post.html", new_ctx(request, {"form": form}))


def search_post(request):
    """
    Vista para buscar publicaciones.

    Esta vista maneja la búsqueda de posts utilizando un formulario. Si el formulario es válido,
    se generan los resultados y se muestran en la plantilla correspondiente.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Redirección a la vista de inicio si no se realiza una búsqueda válida
                      o renderización de los resultados de búsqueda.
    """
    form = SearchPostForm(
        request.GET
    )  # Inicializa el formulario con los datos de búsqueda

    if form.is_valid():  # Verifica la validez del formulario
        input = form.cleaned_data["input"]  # Obtiene el término de búsqueda
        results = buscador.generate_query_set(input).execute()  # Realiza la búsqueda

        ctx = new_ctx(
            request, {"posts": results[:10]}
        )  # Crea el contexto con los resultados
        return render(request, "pages/home.html", context=ctx)

    # Redirige a la vista de inicio si no hay búsqueda válida
    return redirect("home")


@login_required
def favorite_post(request, id):
    """
    Vista para marcar o desmarcar un post como favorito.

    Esta vista maneja la acción de agregar o quitar un post de la lista de favoritos
    del usuario actual.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a marcar como favorito.

    Returns:
        HttpResponse: Respuesta HTTP con un código de estado 204 (sin contenido).
    """
    post = get_object_or_404(Post, pk=id)  # Obtiene el post o devuelve un error 404

    if post.favorites.filter(
        id=request.user.id
    ).exists():  # Verifica si el post ya es favorito
        post.favorites.remove(
            request.user
        )  # Elimina al usuario de la lista de favoritos
    else:
        post.favorites.add(request.user)  # Agrega al usuario a la lista de favoritos

    return HttpResponse(status=204)  # Devuelve un código de estado 20


@login_required
def favorite_list(request):
    """
    Vista para listar los posts favoritos del usuario.

    Esta vista obtiene y muestra todos los posts que el usuario ha marcado como favoritos.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/posts_favorites_list.html'.
    """
    posts_favorites = Post.objects.filter(
        favorites=request.user
    )  # Obtiene los posts favoritos del usuario

    ctx = new_ctx(
        request, {"posts_favorites": posts_favorites}
    )  # Crea el contexto con los posts favoritos
    return render(
        request, "pages/posts_favorites_list.html", ctx
    )  # Renderiza la plantilla correspondiente
