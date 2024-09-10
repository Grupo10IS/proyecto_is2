from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseBadRequest
from django.shortcuts import HttpResponse, get_object_or_404, get_object_or_404, redirect, render

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (
    POST_CREATE_PERMISSION,
    POST_DELETE_PERMISSION,
)
from modulos.Categories.models import Category
from modulos.Posts.forms import NewPostForm
from modulos.Posts.models import Post
from modulos.utils import new_ctx


def home_view(req):
    """
    Vista de inicio 'home_view'.

    Esta vista verifica si el usuario está autenticado y obtiene todos sus permisos.
    Dependiendo de los permisos del usuario, agrega nombres específicos a la lista 'sitios' para
    determinar qué secciones o funcionalidades se deben mostrar en la página de inicio.

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
    Utiliza el modelo 'Post' para recuperar la instancia específica que se va a mostrar y
    utiliza la plantilla 'posts/post_detail.html' para renderizar el contenido.

    Attributes:
        model (Model): El modelo utilizado por la vista ('Post').
        template_name (str): La plantilla HTML utilizada para renderizar el detalle de la publicación.
        context_object_name (str): El nombre de la variable de contexto que representa el objeto 'Post'.
    """

    post = get_object_or_404(Post, id=id)
    # parse tags
    tags = post.tags.split(",") if post.tags else []
    tags = [tag.strip() for tag in tags]  # Remove leading/trailing whitespace

    ctx = new_ctx(
        request,
        {
            "post": post,
            "tags": tags,
            "categories": Category.objects.all(),
        },
    )
    return render(request, "pages/post_detail.html", context=ctx)


@login_required
@permissions_required([POST_CREATE_PERMISSION])
def create_post(request):
    if request.method == "POST":
        post = NewPostForm(request.POST, request.FILES)
        if not post.is_valid():
            print(post.is_valid())
            print(post.errors)
            return HttpResponseBadRequest("Datos proporcionados invalidos")

        p = post.save(commit=False)
        p.author = request.user
        p.save()
        return redirect("/posts/" + str(p.id))

    ctx = new_ctx(request, {"form": NewPostForm})

    return render(
        request,
        "pages/new_post.html",
        context=ctx,
    )


# Vista para listar posts
@login_required
@permissions_required([POST_CREATE_PERMISSION])
def manage_post(request):
    posts = Post.objects.filter(author=request.user)
    ctx = new_ctx(request, {"posts": posts})
    return render(request, "pages/post_list.html", ctx)


# Vista para eliminar un post
@login_required
@permissions_required([POST_DELETE_PERMISSION])
def delete_post(request, id):
    print("POSTID:", id)
    post = get_object_or_404(Post, pk=id)

    if request.method == "POST":
        post.delete()
        return redirect("post_list")
    else:
        print("asndkadbasbk")

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})
    return render(request, "pages/post_confirm_delete.html", ctx)
