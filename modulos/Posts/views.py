import difflib
from datetime import timedelta

from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import AnonymousUser, Group
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.query_utils import Q
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (KANBAN_VIEW_PERMISSION,
                                               POST_APPROVE_PERMISSION,
                                               POST_CREATE_PERMISSION,
                                               POST_DELETE_PERMISSION,
                                               POST_EDIT_PERMISSION,
                                               POST_PUBLISH_PERMISSION,
                                               POST_REJECT_PERMISSION,
                                               POST_REVIEW_PERMISSION,
                                               user_has_access_to_category)
from modulos.Authorization.roles import ADMIN
from modulos.Categories.models import Category
from modulos.Posts.buscador import buscador
from modulos.Posts.disqus import get_disqus_stats
from modulos.Posts.forms import NewPostForm, SearchPostForm
from modulos.Posts.models import Log, NewVersion, Post, Version
from modulos.utils import new_ctx


def home_view(req):
    """
    Vista de inicio 'home_view'.

    Combina:
    - Paginación de los posts recientes.
    - El post destacado.
    - Categorías populares.
    - Posts populares.
    También maneja la búsqueda de posts a través del formulario.
    """

    form = SearchPostForm(req.GET or None)  # Inicializa el formulario de búsqueda

    # Obtener el post con más favoritos
    post_destacado = (
        Post.objects.filter(status=Post.PUBLISHED)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")
        .first()
    )

    # Obtener las tres categorías con más posts marcados como favoritos
    categorias_populares = (
        Category.objects.filter(post__status=Post.PUBLISHED)
        .annotate(favorite_count=Count("post__favorites"))
        .order_by("-favorite_count")[:3]
    )

    # Obtener los 5 posts más populares (con más favoritos)
    posts_populares = (
        Post.objects.filter(status=Post.PUBLISHED)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")[:5]
    )

    # Si hay búsqueda activa
    if form.is_valid() and form.cleaned_data.get("input"):
        input_search = form.cleaned_data["input"]
        posts_recientes = buscador.generate_query_set(input_search).execute()
    else:
        # Obtener los posts publicados más recientes
        posts_recientes = Post.objects.filter(status=Post.PUBLISHED).order_by(
            "-publication_date"
        )

    # Configuración de paginación (10 posts por página)
    paginator = Paginator(posts_recientes, 10)

    try:
        page = int(req.GET.get("page", 1))
    except ValueError:
        page = 1

    if page <= 0:
        page = 1

    # Obtener los posts de la página actual
    posts_paginados = paginator.get_page(page)

    # Crear el contexto
    ctx = new_ctx(
        req,
        {
            "post_destacado": post_destacado,
            "categorias_populares": categorias_populares,
            "posts_recientes": posts_paginados,  # Los posts paginados o resultados de búsqueda
            "posts_populares": posts_populares,
            "form": form,  # Pasar el formulario de búsqueda
        },
    )

    # Agregar los enlaces de página siguiente y anterior
    if posts_paginados.has_next():
        ctx.update({"next_page": posts_paginados.next_page_number()})

    if posts_paginados.has_previous():
        ctx.update({"previous_page": posts_paginados.previous_page_number()})

    return render(req, "pages/home.html", context=ctx)


def view_post(request, id):
    """
    Vista de detalle de publicación 'PostDetailView'.

    Esta vista muestra los detalles de un solo objeto 'Post'.
    Utiliza el modelo 'Post' para recuperar la instancia específica y renderiza el contenido
    utilizando la plantilla 'posts/post_detail.html'.
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
    category = post.category

    # Si la categoría es gratis, mostrar el post completo sin restricción
    if category.tipo == category.GRATIS:
        # Mostrar el detalle completo del post
        tags = post.tags.split(",") if post.tags else []
        tags = [tag.strip() for tag in tags]

        # Verifica si el post es favorito del usuario actual
        es_favorito = (
            post.favorites.filter(id=user.id).exists()
            if user.is_authenticated
            else False
        )

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

    # Si el usuario no está autenticado, mostrar la previsualización
    if isinstance(user, AnonymousUser) or (
        user.is_authenticated and not user_has_access_to_category(user, category)
    ):
        preview_content = post.content.split()[
            :50
        ]  # Truncar a las primeras 50 palabras
        preview_content = " ".join(preview_content) + "..."
        modal_message = None

        # Mensaje diferente según el tipo de categoría
        if isinstance(user, AnonymousUser):
            modal_message = (
                "Para poder ver esta publicación debes iniciar sesión o registrarte."
            )
        elif category.tipo == category.PREMIUM:
            modal_message = "No tienes acceso a esta publicación. Debes suscribirte para poder ver el contenido pagando 1$."
        elif category.tipo == category.SUSCRIPCION:
            modal_message = (
                "Para poder ver esta publicación debes ser suscriptor de nuestra web."
            )

        return render(
            request,
            "pages/post_preview.html",
            {
                "post": post,
                "category": category,
                "preview_content": preview_content,
                "modal_message": modal_message,
            },
        )

    # Si el usuario tiene acceso, mostrar el detalle completo del post
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

    if is_admin:
        posts = Post.objects.all()
    else:
        posts = Post.objects.filter(author=request.user)

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

    if (
        not request.user.has_perm(POST_DELETE_PERMISSION)
        and post.author != request.user
    ):
        return HttpResponseForbidden("No tienes permiso para eliminar este post.")

    if request.method == "POST":
        post.delete()
        return redirect("post_list")

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})
    return render(request, "pages/post_confirm_delete.html", ctx)


@login_required
@permissions_required([POST_EDIT_PERMISSION])
def edit_post(request, id):
    """
    Vista para editar un post existente.

    Esta vista carga el formulario con los datos del post y procesa la actualización
    si se envían nuevos datos.

    Cuando se realiza una modificacion de un post y el mismo se encuentra en cualquier estado
    que no sea borrador, entonces se guarda una version del estado anterior del post a modo de historial de
    cambios.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a editar.

    Returns:
        HttpResponse: Redirección a la lista de posts o renderización del formulario con los datos del post.
    """
    post = get_object_or_404(Post, pk=id)

    if request.method == "POST":

        form = NewPostForm(request.POST, request.FILES, instance=post)

        if not form.is_valid():
            # FIX: mostrar errores en el editor
            return HttpResponseBadRequest(f"Formulario inválido")

        # guardar version anterior del post
        version = NewVersion(post)
        version.save()

        post.save()
        post.version += 1
        post.save()

        return redirect("post_list")

    form = NewPostForm(instance=post)
    return render(request, "pages/new_post.html", new_ctx(request, {"form": form}))


def enhanced_search(request):
    form = SearchPostForm(request.GET)

    if not form.is_valid():
        return redirect("home")

    input = form.cleaned_data["input"]
    results = buscador.generate_query_set(input).execute()

    ctx = new_ctx(
        request, {"posts": results, "form": SearchPostForm(initial={"input": input})}
    )
    return render(request, "pages/search_results.html", context=ctx)


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

    return redirect("post_detail", id=id)


# --------------------
# Flujo de publicacion
# --------------------


@login_required
@permissions_required([KANBAN_VIEW_PERMISSION])
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
                # permisos para mostrar las acciones sobre las publicaciones
                "can_create": request.user.has_perm(POST_CREATE_PERMISSION),
                "can_publish": request.user.has_perm(POST_PUBLISH_PERMISSION),
                "can_approve": request.user.has_perm(POST_APPROVE_PERMISSION),
                "can_reject": request.user.has_perm(POST_REJECT_PERMISSION),
            },
        ),
    )


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


# --------------------
#      Varios
# --------------------


@login_required
def favorite_list(request):
    """
    Vista para listar los posts favoritos del usuario y las categorías de interés.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/posts_favorites_list.html'.
    """
    # Obtener los posts favoritos
    posts_favorites = Post.objects.filter(favorites=request.user)

    # Paginación: 5 posts por página
    paginator = Paginator(posts_favorites, 5)  # 5 posts por página
    page_number = request.GET.get("page")  # Obtiene el número de la página actual
    posts_favorites_paginados = paginator.get_page(page_number)  # Paginación

    # Obtener las categorías de los posts favoritos (sin duplicados)
    categorias_interes = Category.objects.filter(
        post__favorites=request.user
    ).distinct()

    ctx = new_ctx(
        request,
        {
            "posts_favorites": posts_favorites_paginados,  # Pasamos la lista paginada
            "categorias_interes": categorias_interes,  # Pasar las categorías al contexto
        },
    )
    return render(request, "pages/posts_favorites_list.html", ctx)


def list_contenidos_view(request):
    """
    Vista para listar todos los contenidos por categoría con opción de búsqueda y filtrado.
    """
    categories = Category.objects.filter(post__status=Post.PUBLISHED).distinct()

    # Inicializa el formulario de búsqueda con los parámetros GET si existen
    form = SearchPostForm(request.GET or None)

    # Construimos un query dinámico para los filtros
    posts_query = Post.objects.filter(status=Post.PUBLISHED)

    # Aplicar filtros si el formulario es válido
    if form.is_valid():
        # Filtro por palabra clave en el título o contenido
        input_search = form.cleaned_data.get("input")
        if input_search:
            posts_query = posts_query.filter(Q(title__icontains=input_search))

        # Filtro por categoría
        category = form.cleaned_data.get("category")
        if category:
            posts_query = posts_query.filter(category=category)

        # Filtro por autor
        author = form.cleaned_data.get("author")
        if author:
            posts_query = posts_query.filter(author__username__icontains=author)

        # Filtro por fecha de publicación
        publication_date = form.cleaned_data.get("publication_date")
        if publication_date:
            posts_query = posts_query.filter(publication_date=publication_date)

    # Crear un diccionario para almacenar los posts paginados por categoría
    posts_by_category = {}
    for category in categories:
        filtered_posts = posts_query.filter(category=category)

        # Paginación: 6 posts por página para cada categoría
        paginator = Paginator(filtered_posts, 6)  # 6 posts por página
        page_number = request.GET.get(
            f"page_{category.id}", 1
        )  # Se captura la página de cada categoría
        page_obj = paginator.get_page(page_number)

        if filtered_posts.exists():
            posts_by_category[category] = page_obj

    # Crear el contexto y pasarlo a la plantilla
    ctx = {
        "posts_by_category": posts_by_category,
        "form": form,  # Pasar el formulario al contexto
    }

    return render(request, "pages/list_contenidos.html", ctx)


# --------------------
#    Estadisticas
# --------------------


@login_required
def post_log_list(request, id):
    post = get_object_or_404(Post, pk=id)

    if not request.user.has_perm(POST_REVIEW_PERMISSION) or post.author != request.user:
        return HttpResponseForbidden(
            "No tienes permisos para acceder a los logs de este post"
        )

    logs = Log.objects.filter(post=post).order_by("-creation_date")

    return render(request, "pages/logs_list.html", new_ctx(request, {"logs": logs}))


@login_required
@permissions_required([POST_REVIEW_PERMISSION])
def post_versions_list(request, id):
    get_object_or_404(Post, pk=id)

    versions = Version.objects.filter(post_id=id)
    ctx = new_ctx(request, {"versions": versions})

    return render(request, "pages/post_versions_list.html", ctx)


@login_required
@permissions_required([POST_REVIEW_PERMISSION])
def post_version_detail(request, post_id, version):
    original = get_object_or_404(Post, pk=post_id)

    if (
        not request.user.has_perm(POST_REVIEW_PERMISSION)
        or original.author != request.user
    ):
        return HttpResponseForbidden(
            "No tienes permisos para acceder a las versiones de este post"
        )

    version = get_object_or_404(Version, version=version, post_id=original.id)

    post_content = original.content.splitlines()
    version_content = version.content.splitlines()

    diff = difflib.unified_diff(
        version_content,
        post_content,
        fromfile="Comparacion.md",
        tofile="Comparacion.md",
        lineterm="",
    )

    diff = "\n".join(list(diff))

    # Pasamos el diff a la plantilla
    ctx = new_ctx(
        request,
        {"original": original, "version": version, "diff_content": diff},
    )

    return render(request, "pages/post_version_detail.html", ctx)


@login_required
@permission_required([POST_CREATE_PERMISSION])
# FIX: cambiar los permisos para que solo el autor y algunos puedan ver esas Estadisticas
def post_statistics(request, id):
    post = get_object_or_404(Post, pk=id)

    ctx = new_ctx(
        request,
        {
            "post": post,
            "logs": Log.objects.filter(post=post)[:5],
            "versions": Version.objects.filter(post_id=post.id)[:5],
            "disqus": get_disqus_stats(post.id)
        },
    )

    return render(request, "pages/statistics.html", ctx)
