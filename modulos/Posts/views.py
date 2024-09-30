from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, Group
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (POST_APPROVE_PERMISSION,
                                               POST_CREATE_PERMISSION,
                                               POST_DELETE_PERMISSION,
                                               POST_EDIT_PERMISSION,
                                               POST_PUBLISH_PERMISSION,
                                               POST_REJECT_PERMISSION,
                                               POST_REVIEW_PERMISSION,
                                               user_has_access_to_category)
from modulos.Authorization.roles import ADMIN
from modulos.Categories.models import Category
from modulos.Pagos.models import Payment
from modulos.Posts.buscador import buscador
from modulos.Posts.forms import NewPostForm, SearchPostForm
from modulos.Posts.models import Post
from modulos.UserProfile.models import UserProfile
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
    ctx = new_ctx(req, {"posts": Post.objects.filter(status=Post.PUBLISHED)[:20]})
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
    post = get_object_or_404(Post, id=id)

    # Permitir ver la publicación solo si está publicada o si el usuario es el autor o tiene permisos
    if (
        post.status != Post.PUBLISHED
        and post.author != request.user
        and not request.user.has_perm(POST_REVIEW_PERMISSION)
    ):
        return HttpResponseBadRequest("No tienes permiso para ver esta publicación.")

    # administrar acceso a categorias moderadas o de pago
    user = request.user
    category = get_object_or_404(Category, pk=post.category.id)

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

    # parse tags
    tags = post.tags.split(",") if post.tags else []
    tags = [tag.strip() for tag in tags]

    # Verifica si el post es favorito del usuario actual
    es_favorito = post.favorites.filter(id=request.user.id).exists()

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
        form = NewPostForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest("Datos proporcionados invalidos")

        p = form.save(commit=False)
        if "save_draft" in request.POST:
            p.status = Post.DRAFT
        elif "submit_review" in request.POST:
            p.status = Post.PENDING_REVIEW  # Estado "Pendiente de Revisión"

        p.author = request.user
        p.save()

        return redirect("/posts/" + str(p.id))

    ctx = new_ctx(request, {"form": NewPostForm})
    return render(
        request,
        "pages/new_post.html",
        context=ctx,
    )


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
    is_admin = Group.objects.filter(name=ADMIN, user=request.user).exists()
    posts = Post.objects.all() if is_admin else Post.objects.filter(author=request.user)

    # Obtiene todos los permisos del usuario
    permisos = request.user.get_all_permissions()

    perm_create = "UserProfile." + POST_CREATE_PERMISSION in permisos
    perm_edit = "UserProfile." + POST_EDIT_PERMISSION in permisos
    perm_delete = "UserProfile." + POST_DELETE_PERMISSION in permisos

    ctx = new_ctx(
        request,
        {
            "posts": posts,
            "perm_create": request.user.has_perm(POST_CREATE_PERMISSION),
            "perm_edit": request.user.has_perm(POST_EDIT_PERMISSION),
            "perm_delete": request.user.has_perm(POST_DELETE_PERMISSION),
        },
    )
    return render(request, "pages/post_list.html", ctx)


@login_required
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
    post: Post = get_object_or_404(Post, pk=id)

    if not request.user.has_perm(POST_DELETE_PERMISSION) and post.author != request.user:
        return HttpResponseForbidden("No tienes permiso para eliminar este post.")

    if request.method == "POST":
        post.delete()  # Elimina el post
        return redirect("post_list")  # Redirige a la lista de posts

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})  # Crea el contexto con el post a eliminar
    return render(request, "pages/post_confirm_delete.html", ctx)


@login_required
@permissions_required([POST_EDIT_PERMISSION])
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
    post = get_object_or_404(Post, pk=id)
    if request.method == "POST":
        form = NewPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            p = form.save(commit=False)

            if "save_draft" in request.POST:
                p.status = Post.DRAFT
            elif "submit_review" in request.POST:
                p.status = Post.PENDING_REVIEW  # Estado "Pendiente de Revisión"

            p.save()

            return redirect("post_list")

    form = NewPostForm(instance=post)
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

    # Si el post ya es favorito lo agrega, si no lo elimina
    if not post.favorites.filter(id=request.user.id).exists():
        post.favorites.add(request.user)
    else:
        post.favorites.remove(request.user)

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
    posts_favorites = Post.objects.filter(favorites=request.user)
    ctx = new_ctx(request, {"posts_favorites": posts_favorites})
    return render(request, "pages/posts_favorites_list.html", ctx)


# --------------------
# Flujo de publicacion
# --------------------


@login_required
@permissions_required([POST_CREATE_PERMISSION])
def send_to_review(request, id):
    post = get_object_or_404(Post, id=id)
    post.status = Post.PENDING_REVIEW
    post.save()
    return redirect("kanban_board")


@login_required
@permissions_required([POST_APPROVE_PERMISSION])
def aprove_post(request, id):
    post = get_object_or_404(Post, id=id)
    post.status = Post.PENDING_PUBLICATION
    post.save()
    return redirect("kanban_board")


@login_required
@permissions_required([POST_PUBLISH_PERMISSION])
def publish_post(request, id):
    post = get_object_or_404(Post, id=id)
    post.status = Post.PUBLISHED
    post.publication_date = timezone.now()
    post.save()
    return redirect("kanban_board")


@login_required
@permissions_required([POST_REJECT_PERMISSION])
def reject_post(request, id):
    post = get_object_or_404(Post, id=id)
    post.status = Post.DRAFT
    post.save()
    return redirect("kanban_board")


@login_required
def kanban_board(request):
    # Filtrar los posts según el estado
    drafts = Post.objects.filter(status=Post.DRAFT, author=request.user)
    pending_review = Post.objects.filter(status=Post.PENDING_REVIEW)
    pending_publication = Post.objects.filter(status=Post.PENDING_PUBLICATION)
    recently_published = Post.objects.filter(
        status=Post.PUBLISHED,
        publication_date__gte=timezone.now() - timedelta(days=5),
    )

    # Pasar las publicaciones a la plantilla para organizarlas en el tablero
    return render(
        request,
        "pages/kanban_board.html",
        new_ctx(
            request,
            {
                "drafts": drafts,
                "pending_review": pending_review,
                "pending_publication": pending_publication,
                "published": recently_published,
                # permisos para mostrar los botones
                "can_create": request.user.has_perm(POST_CREATE_PERMISSION),
                "can_publish": request.user.has_perm(POST_PUBLISH_PERMISSION),
                "can_approve": request.user.has_perm(POST_APPROVE_PERMISSION),
                "can_reject": request.user.has_perm(POST_REJECT_PERMISSION),
            },
        ),
    )


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
