from django.forms import CharField, forms
from django.forms.models import ModelForm
from django.shortcuts import HttpResponse, redirect, render
from django.views.generic import DetailView
from markdown import Markdown

from modulos.Categories.models import Category
from modulos.Posts.forms import NewPostForm
from modulos.Posts.models import Post


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

    sitios = []
    if req.user.is_authenticated:
        permisos = req.user.get_all_permissions()

        # Itera sobre los permisos
        for perm in permisos:
            if "user" in perm and perm not in sitios:
                sitios.append("user")
            if "post" in perm and perm not in sitios:
                sitios.append("post")
            if "categor" in perm and perm not in sitios:
                sitios.append("category")
            if "role" in perm and perm not in sitios:
                sitios.append("role")

    return render(
        req,
        "pages/home.html",
        context={
            "categories": Category.objects.all(),
            "posts": Post.objects.all()[:10],
            "sitios": sitios,
        },
    )


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
        md = Markdown(extensions=["fenced_code"])
        post.content = md.convert(post.content)
        context = {
            "post": post,
            "categories": Category.objects.all(),
        }
        return render(request, "pages/post_detail.html", context=context)

    return HttpResponse("No se encontro el post al que quiere acceder")


def create_post(request):
    if request.method == "POST":
        post = NewPostForm(request.POST)
        if post.is_valid():
            post.save()
            return redirect("profile")

    return render(
        request,
        "pages/markdown.html",
        context={"form": NewPostForm},
    )
