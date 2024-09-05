from django.shortcuts import HttpResponse, redirect, render

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

    post = Post.objects.get(id=id)
    if post != None:
        ctx = new_ctx(
            request,
            {
                "post": post,
                "categories": Category.objects.all(),
            },
        )
        return render(request, "pages/post_detail.html", context=ctx)

    return HttpResponse("No se encontro el post al que quiere acceder")


def create_post(request):
    if request.method == "POST":
        post = NewPostForm(request.POST)
        if post.is_valid():
            post.save()
            return redirect("profile")

    ctx = new_ctx(request, {"form": NewPostForm})

    return render(
        request,
        "pages/markdown.html",
        context=ctx,
    )
