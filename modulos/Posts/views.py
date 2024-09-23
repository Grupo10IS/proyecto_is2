from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponseBadRequest
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from modulos.Authorization.roles import ADMIN
from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (
    POST_CREATE_PERMISSION,
    POST_DELETE_PERMISSION,
    POST_EDIT_PERMISSION,
)
from modulos.UserProfile.models import UserProfile
from modulos.Categories.models import Category
from modulos.Posts.buscador import buscador
from modulos.Posts.forms import NewPostForm, SearchPostForm
from modulos.Posts.models import Post
from modulos.utils import new_ctx
from modulos.Authorization.permissions import user_has_access_to_category
from modulos.Pagos.models import Payment
from django.contrib.auth.models import AnonymousUser
from django.views.generic import TemplateView

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

    ctx = new_ctx(req, {"posts": Post.objects.all()[:20]})

    return render(req, "pages/home.html", context=ctx)


def view_post(request, id):
    post = get_object_or_404(Post, id=id)
    user = request.user
    category = post.category

    # Si el usuario no está autenticado
    if isinstance(user, AnonymousUser):
        # Mostrar modal de acceso denegado para categorías premium y de suscripción
        if category.tipo in [category.PREMIUM, category.SUSCRIPCION]:
            return render(
                request,
                "access_denied_modal.html",
                {
                    "category": category,
                    "modal_message": "Para poder ver esta publicación debes iniciar sesión o registrarte.",
                },
            )

    # Si el usuario está autenticado, verificar acceso a la categoría del post
    if user.is_authenticated and not user_has_access_to_category(user, category):
        if category.tipo == category.PREMIUM:
            # Verificar si el usuario ha completado un pago para esta categoría
            if not Payment.objects.filter(
                user=user, category=category, status="completed"
            ).exists():
                # Mostrar mensaje de pago necesario para ver el post
                return render(
                    request,
                    "access_denied_modal.html",
                    {
                        "category": category,
                        "modal_message": "No tienes acceso a esta publicación. Debes suscribirte para poder ver el contenido pagando 1$.",
                    },
                )
        elif category.tipo == category.SUSCRIPCION:
            # Mostrar mensaje de suscripción necesaria
            return render(
                request,
                "access_denied_modal.html",
                {
                    "category": category,
                    "modal_message": "Para poder ver esta publicación debes ser suscriptor de nuestra web.",
                },
            )

    # Si el usuario tiene acceso o la categoría es gratis, mostrar el detalle del post
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
@permissions_required(
    [POST_CREATE_PERMISSION, POST_EDIT_PERMISSION, POST_DELETE_PERMISSION]
)
def manage_post(request):
    # Verifica si el usuario pertenece al grupo 'Administrador'
    is_admin = Group.objects.filter(name=ADMIN, user=request.user).exists()

    if is_admin:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(author=request.user)

    permisos = request.user.get_all_permissions()

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


# Vista para eliminar un post
@login_required
@permissions_required([POST_DELETE_PERMISSION])
def delete_post(request, id):
    post = get_object_or_404(Post, pk=id)

    if request.method == "POST":
        post.delete()
        return redirect("post_list")

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})
    return render(request, "pages/post_confirm_delete.html", ctx)


# Vista para editar un post
@login_required
@permissions_required([POST_EDIT_PERMISSION, POST_CREATE_PERMISSION])
def edit_post(request, id):
    post = get_object_or_404(Post, pk=id)
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect("post_list")

    form = NewPostForm(instance=post)
    return render(request, "pages/new_post.html", new_ctx(request, {"form": form}))


def search_post(request):
    form = SearchPostForm(request.GET)

    if form.is_valid():
        input = form.cleaned_data["input"]
        results = buscador.generate_query_set(input).execute()

        ctx = new_ctx(request, {"posts": results[:10]})
        return render(request, "pages/home.html", context=ctx)

    else:
        # O redirige a donde sea apropiado si no hay búsqueda
        return redirect("home")


class ContenidosView(TemplateView):
    template_name = "pages/list_contenidos.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtener todas las categorías
        categories = Category.objects.all()
        # Crear un diccionario para almacenar los posts por categoría
        posts_by_category = {
            category: Post.objects.filter(category=category) for category in categories
        }
        context["posts_by_category"] = posts_by_category
        return context
