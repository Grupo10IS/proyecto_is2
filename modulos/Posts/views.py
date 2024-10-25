import difflib
from datetime import timedelta

from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser, Group
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.query_utils import Q
from django.http.response import (HttpResponseBadRequest,
                                  HttpResponseForbidden, HttpResponseRedirect)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

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
from modulos.Posts.forms import NewPostForm, PostsListFilter, SearchPostForm
from modulos.Posts.models import (Log, Post, RestorePost, Version,
                                  new_creation_log, new_edition_log)
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
        Post.objects.filter(status=Post.PUBLISHED, active=True)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")
        .first()
    )

    # Obtener las tres categorías con más posts marcados como favoritos
    categorias_populares = (
        Category.objects.filter(post__status=Post.PUBLISHED, post__active=True)
        .annotate(favorite_count=Count("post__favorites"))
        .order_by("-favorite_count")[:3]
    )

    # Obtener los 5 posts más populares (con más favoritos)
    posts_populares = (
        Post.objects.filter(status=Post.PUBLISHED, active=True)
        .annotate(favorite_count=Count("favorites"))
        .order_by("-favorite_count")[:5]
    )

    # Si hay búsqueda activa
    if form.is_valid() and form.cleaned_data.get("input"):
        input_search = form.cleaned_data["input"]
        posts_recientes = buscador.generate_query_set(input_search).execute()
    else:
        # Obtener los posts publicados más recientes
        posts_recientes = Post.objects.filter(
            status=Post.PUBLISHED, active=True
        ).order_by("-publication_date")

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
    # Verificacion de permanencia de validez del post
    if (
        post.expiration_date
        and timezone.now() > post.expiration_date
        and post.author != request.user
    ):
        return HttpResponseBadRequest("Este post ha expirado y no está disponible.")

    # Permitir ver la publicación solo si está publicada o si el usuario es el autor o tiene permisos
    if (
        (post.status != Post.PUBLISHED or not post.active)
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
            new_ctx(
                request,
                {
                    "post": post,
                    "category": category,
                    "preview_content": preview_content,
                    "modal_message": modal_message,
                },
            ),
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
@permissions_required(
    [POST_CREATE_PERMISSION, POST_EDIT_PERMISSION, POST_DELETE_PERMISSION]
)
def manage_posts(request):
    """
    Vista para gestionar los posts.

    Esta vista lista todos los posts del usuario actual o de todos los usuarios
    si el usuario pertenece al grupo 'Administrador'.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/post_list.html'.
    """
    # FIX: solucionar esta parte y repensar los permisos para ver, porque no puede
    # ser que esta verificacion esta acoplada al ROL admin y no a algun permiso (OJO: podemos
    # tener roles personalizados ACUERDENSE).
    is_admin = Group.objects.filter(name=ADMIN, user=request.user).exists()
    posts = (
        Post.objects.filter(active=True, status=Post.PUBLISHED)
        if is_admin
        else Post.objects.filter(author=request.user, active=True)
    )

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


def manage_inactive_posts(request):
    """
    Vista para gestionar los posts inactivos.

    Esta vista lista todos los posts inactivos del usuario actual o de todos los usuarios
    si el usuario pertenece al grupo 'Administrador'.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: La respuesta HTTP con el contenido renderizado de la plantilla 'pages/post_list.html'.
    """
    can_delete = request.user.has_perm(POST_DELETE_PERMISSION)

    posts = (
        Post.objects.filter(active=False)
        if can_delete
        else Post.objects.filter(author=request.user, active=False)
    )

    ctx = new_ctx(
        request,
        {"posts": posts, "can_delete": can_delete},
    )

    return render(request, "pages/inactives_list.html", ctx)


# ----------------
# Operaciones CRUD
# ----------------


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
        if form.is_valid():
            p = form.save(commit=False)
            author = request.user
            p.author = author

            # Validar fechas dentro de la vista
            if p.publication_date is None:
                p.publication_date = timezone.now()

            if p.expiration_date and p.expiration_date <= p.publication_date:
                form.add_error(
                    "expiration_date",
                    "La fecha de validez no puede ser anterior o igual a la fecha de publicación.",
                )

                # Renderizar de nuevo el formulario con el error agregado
                ctx = new_ctx(request, {"form": form})
                return render(request, "pages/new_post.html", context=ctx)

            p.save()

            # Actualizar la cantidad de posts creados por el autor
            author.c_creados += 1
            author.save()

            new_creation_log(post=p, user=author)

            return redirect("/posts/" + str(p.id))

        # Si el formulario no es válido, mostrar los errores en el template
        ctx = new_ctx(request, {"form": form})
        return render(request, "pages/new_post.html", context=ctx)

    form = NewPostForm()
    ctx = new_ctx(request, {"form": form})
    return render(request, "pages/new_post.html", context=ctx)


@login_required
def inactivate_post(request, id):
    """
    Vista para inactivar un post.

    Esta vista muestra un mensaje de confirmación antes de inactivar un post.
    Si la solicitud es un POST, se elimina el post y se redirige a la lista de posts.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a inactivar.

    Returns:
        HttpResponse: Redirección a la lista de posts o renderización de la confirmación de eliminación.
    """
    post: Post = get_object_or_404(Post, pk=id)

    # Verifica si la acción proviene de un reporte
    if request.GET.get("from_report") == "true":
        # Actualiza is_handled a True para todos los reportes relacionados con el post
        post.reports.update(is_handled=True)

    if (
        not request.user.has_perm(POST_DELETE_PERMISSION)
        and post.author != request.user
    ):
        return HttpResponseForbidden("No tienes permiso para inactivar este post.")

    if request.method == "POST":
        post.active = False
        post.save()

        Log(post=post, message=f"Post inactivado por: {request.user.username}").save()

        request.user.c_audit_eliminados += 1
        request.user.save()

        return redirect("post_list")

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})
    return render(request, "pages/post_confirm_delete.html", ctx)


def reactivate_post(request, id):
    """
    Vista para reactivar un post.

    Esta vista vuelve a activar un post que estaba inactivado. Solo aquellos que pueden inactivar
    un post pueden volver a reactivarlo.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        id (int): El ID del post a inactivar.

    Returns:
        HttpResponse: Redirección a la lista de posts o renderización de la confirmación de eliminación.
    """
    post: Post = get_object_or_404(Post, pk=id)

    if not request.user.has_perm(POST_DELETE_PERMISSION):
        return HttpResponseForbidden(
            "No tienes permiso para reactivar este post. Contacta con un administrador"
        )

    if request.method == "POST":
        post.active = True
        post.save()

        Log(post=post, message=f"Post reactivado por: {request.user.username}").save()

        request.user.c_audit_eliminados += 1
        request.user.save()

        return redirect("post_list")

    # Si no es una solicitud POST, muestra un mensaje de confirmación
    ctx = new_ctx(request, {"post": post})
    return render(request, "pages/post_confirm_reactivation.html", ctx)


@login_required
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
    old_instance = get_object_or_404(Post, pk=id)

    if not post.active:
        return HttpResponseForbidden("No se puede editar un post inactivo")

    if request.method == "POST":

        form = NewPostForm(request.POST, request.FILES, instance=post)

        if not form.is_valid():
            # Si el formulario no es válido, mostrar los errores en el template
            ctx = new_ctx(request, {"form": form})
            return render(request, "pages/new_post.html", context=ctx)

        # guardar el post con la version actualizada
        post.version += 1
        # Verificar fechas durante edicion
        if post.expiration_date and post.expiration_date <= post.publication_date:
            form.add_error(
                "expiration_date",
                "La fecha de expiracion no puede ser menor a la de publicacion",
            )
            ctx = new_ctx(request, {"form": form})
            return render(request, "pages/new_post.html", context=ctx)

        post.save()

        # generar un registro en los logs
        new_edition_log(old_instance=old_instance, new_instance=post, user=request.user)

        return redirect("post_list")

    # no permitir editar posts ya publicados
    if post.status == post.PUBLISHED:
        return HttpResponseBadRequest(f"No se puede editar un post ya publicado")

    # solo permitir a editores editar cuando esta pendiente de revision.
    if post.status == post.PENDING_REVIEW and not request.user.has_perm(
        POST_APPROVE_PERMISSION
    ):
        return HttpResponseBadRequest(
            f"No se puede editar un post pendiente de aprobacion si no eres un editor"
        )

    # solo permitir a publicadores editar cuando esta pendiente de publicacion.
    if post.status == post.PENDING_PUBLICATION and not request.user.has_perm(
        POST_PUBLISH_PERMISSION
    ):
        return HttpResponseBadRequest(
            f"No se puede editar un post pendiente de publicacion si no eres un publicador"
        )

    # solo permitir a los propios autores editar sus borradores.
    if post.status == post.DRAFT and request.user != post.author:
        return HttpResponseBadRequest(f"Solo los autores pueden editar un borrador")

    form = NewPostForm(instance=post)
    return render(request, "pages/new_post.html", new_ctx(request, {"form": form}))


# --------------------
# Flujo de publicacion
# --------------------


@login_required
@permissions_required([KANBAN_VIEW_PERMISSION])
def kanban_board(request):
    """
    Vista para mostrar el tablero Kanban con las publicaciones organizadas por estado.

    Argumentos:
        request: El objeto de solicitud HTTP.

    Retorna:
        Renderiza la página kanban_board con las publicaciones en sus respectivos estados: borradores, pendientes de revisión,
        pendientes de publicación y recientemente publicadas. También pasa los permisos del usuario para determinar las acciones disponibles.
    """
    user = request.user

    # Listar todos los posts o solo los posts si se trata de un publisher/editor
    if (
        user.has_perm(POST_PUBLISH_PERMISSION)
        or user.has_perm(POST_APPROVE_PERMISSION)
        or user.has_perm(POST_REJECT_PERMISSION)
        or user.has_perm(POST_DELETE_PERMISSION)
    ):
        recently_published = Post.objects.filter(
            status=Post.PUBLISHED,
            active=True,
            publication_date__gte=timezone.now() - timedelta(days=5),
        )
        pending_review = Post.objects.filter(active=True, status=Post.PENDING_REVIEW)
        pending_publication = Post.objects.filter(
            active=True, status=Post.PENDING_PUBLICATION
        )

    # De lo contrario listar solo los posts del autor
    else:
        recently_published = Post.objects.filter(
            status=Post.PUBLISHED,
            active=True,
            author=user,
            publication_date__gte=timezone.now() - timedelta(days=5),
        )
        pending_review = Post.objects.filter(
            active=True, status=Post.PENDING_REVIEW, author=user
        )
        pending_publication = Post.objects.filter(
            active=True, status=Post.PENDING_PUBLICATION, author=user
        )

    drafts = Post.objects.filter(status=Post.DRAFT, active=True, author=user)

    # asignar publicacion directa a aquellas publicaciones cuya categoria es de tipo "libre"
    for post in drafts:
        if post.category.moderacion == Category.LIBRE:
            post.__setattr__("can_publish_directly", True)
        else:
            post.__setattr__("can_publish_directly", False)

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
                "can_create": user.has_perm(POST_CREATE_PERMISSION),
                "can_publish": user.has_perm(POST_PUBLISH_PERMISSION),
                "can_approve": user.has_perm(POST_APPROVE_PERMISSION),
                "can_reject": user.has_perm(POST_REJECT_PERMISSION),
            },
        ),
    )


@login_required
@permissions_required([POST_CREATE_PERMISSION])
def send_to_review(request, id):
    """
    Vista para enviar una publicación a revisión.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post que se va a enviar a revisión.

    Retorna:
        Redirige al tablero Kanban una vez que el estado del post se ha actualizado a 'Pendiente de Revisión'.
    """
    post = get_object_or_404(Post, id=id)

    if not post.active:
        return HttpResponseForbidden("No se puede enviar a review un post inactivo")

    post.status = Post.PENDING_REVIEW
    post.save()

    return redirect("kanban_board")


@login_required
@permissions_required([POST_APPROVE_PERMISSION])
def aprove_post(request, id):
    """
    Vista para aprobar una publicación y pasarla al estado de 'Pendiente de Publicación'.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post que se va a aprobar.

    Retorna:
        Redirige al tablero Kanban después de cambiar el estado del post a 'Pendiente de Publicación'.
    """
    post = get_object_or_404(Post, id=id)

    if not post.active:
        return HttpResponseForbidden("No se puede enviar a review un post inactivo")

    post.status = Post.PENDING_PUBLICATION
    post.save()

    # actualizar las estadisticas del editor y el autor
    author = post.author
    editor = request.user

    editor.c_audit_revisados += 1
    author.c_aprobados += 1

    editor.save()
    author.save()

    return redirect("kanban_board")


@login_required
def publish_post(request, id):
    """
    Vista para publicar una publicación.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post que se va a publicar.

    Retorna:
        Redirige al tablero Kanban una vez que el estado del post se ha actualizado a 'Publicado' y se ha registrado la fecha de publicación.
    """
    post = get_object_or_404(Post, id=id)

    if not post.active:
        return HttpResponseForbidden("No se puede publicar un post inactivo")

    category = post.category

    if (
        not request.user.has_perm(POST_PUBLISH_PERMISSION)
        and not category.moderacion == Category.LIBRE
    ):
        return HttpResponseForbidden(
            "No tienes permisos para publicar en esta categoria"
        )

    post.status = Post.PUBLISHED
    post.publication_date = timezone.now()
    post.save()

    # actualizar las estadisticas del publicador y el autor
    author = post.author
    publisher = request.user

    publisher.c_audit_publicados += 1
    author.c_publicados += 1

    publisher.save()
    author.save()

    return redirect("kanban_board")


# Formulario para el motivo de rechazo
class RejectionReasonForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea, label="", required=True)


@login_required
@permissions_required([POST_REJECT_PERMISSION])
def reject_post(request, id):
    """
    Vista para rechazar una publicación y devolverla al estado de 'Borrador'.
    """
    post = get_object_or_404(Post, id=id)

    if not post.active:
        return HttpResponseForbidden("No se puede rechazar un post inactivo")

    if post.status == post.PUBLISHED:
        return HttpResponseForbidden(
            "No puedes tocar el estado de un post ya publicado"
        )

    if request.method == "POST":
        form = RejectionReasonForm(request.POST)
        if form.is_valid():
            # Obtener la razón de rechazo del formulario
            rejection_reason = form.cleaned_data["rejection_reason"]

            # Retrasar un paso el estado de la publicación
            if post.status == post.PENDING_REVIEW:
                post.status = Post.DRAFT
            elif post.status == post.PENDING_PUBLICATION:
                post.status = Post.PENDING_REVIEW

            post.save()

            # Actualizar las estadísticas del auditor y el autor
            author = post.author
            audit = request.user

            audit.c_audit_rechazados += 1
            author.c_rechazados += 1
            audit.save()
            author.save()

            # Registrar el log del rechazo
            Log(
                post=post,
                message=f'El post "{post.title}" ha sido rechazado por "{audit.username}". Motivo: {rejection_reason}.',
            ).save()

            # Enviar el correo de notificación al autor con el motivo del rechazo
            subject = "Tu post ha sido rechazado 😕"
            message = (
                f"Hola {post.author.username}, tu post '{post.title}' ha sido rechazado. "
                f"\nMotivo del rechazo: {rejection_reason}. "
                "\nPor favor, revisa los comentarios o haz los ajustes necesarios antes de volver a enviarlo para revisión."
            )
            send_mail(
                subject,
                message,
                "groupmakex@gmail.com",
                [post.author.email],
                fail_silently=False,
            )

            return redirect("kanban_board")

    else:
        form = RejectionReasonForm()

    context = {"form": form, "post": post}
    return render(request, "pages/reject_post.html", context)


# --------------------
#      Varios
# --------------------


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
    posts_favorites = Post.objects.filter(favorites=request.user, active=True)

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
    categories = Category.objects.filter(
        post__status=Post.PUBLISHED, post__active=True
    ).distinct()

    # Inicializa el formulario de búsqueda con los parámetros GET si existen
    form = PostsListFilter(request.GET or None)

    # Construimos un query dinámico para los filtros
    posts_query = Post.objects.filter(status=Post.PUBLISHED, active=True)

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
    ctx = new_ctx(
        request,
        {
            "posts_by_category": posts_by_category,
            "form": form,  # Pasar el formulario al contexto
        },
    )

    return render(request, "pages/list_contenidos.html", ctx)


# --------------------
#    Estadisticas
# --------------------


@login_required
def post_log_list(request, id):
    """
    Vista para listar los registros de un post específico.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post para obtener sus registros.

    Retorna:
        Renderiza la página logs_list con los registros del post, o devuelve un
        HttpResponseForbidden si el usuario no tiene permisos o no es el autor del post.
    """
    post = get_object_or_404(Post, pk=id)

    if (
        not request.user.has_perm(POST_REVIEW_PERMISSION)
        and post.author != request.user
    ):
        return HttpResponseForbidden(
            "No tienes permisos para acceder a los logs de este post"
        )

    logs = Log.objects.filter(post=post).order_by("-creation_date")

    return render(request, "pages/logs_list.html", new_ctx(request, {"logs": logs}))


@login_required
def post_versions_list(request, id):
    """
    Vista para listar todas las versiones de un post específico.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post para obtener sus versiones.

    Retorna:
        Renderiza la página post_versions_list con las versiones del post.
    """
    post = get_object_or_404(Post, pk=id)

    if (
        not request.user.has_perm(POST_REVIEW_PERMISSION)
        and post.author != request.user
    ):
        return HttpResponseForbidden(
            "No tienes permisos para acceder al registro de versiones de este post"
        )

    versions = Version.objects.filter(post_id=id)
    ctx = new_ctx(request, {"versions": versions})

    return render(request, "pages/post_versions_list.html", ctx)


@login_required
def post_version_detail(request, post_id, version):
    """
    Vista para mostrar detalles y diferencias entre el contenido actual del post y una versión específica.

    Argumentos:
        request: El objeto de solicitud HTTP.
        post_id: El ID del post.
        version: El número de versión del post para comparar.

    Retorna:
        Renderiza la página post_version_detail con las diferencias entre el contenido de la versión y el contenido actual del post.
        Si el usuario no tiene permisos o no es el autor del post, devuelve un HttpResponseForbidden.
    """
    original = get_object_or_404(Post, pk=post_id)

    if (
        not request.user.has_perm(POST_REVIEW_PERMISSION)
        and original.author != request.user
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
def post_revert_version(request, post_id, version):
    """
    Vista para revertir un post a una versión anterior.

    Argumentos:
        request: El objeto de solicitud HTTP.
        post_id: El ID del post que se quiere revertir.
        version: El número de versión a la que se desea revertir el post.

    Retorna:
        Redirige a la lista de versiones del post después de haber restaurado la versión seleccionada.
        Si el usuario no tiene permisos o no es el autor del post, devuelve un HttpResponseForbidden.
    """
    original = get_object_or_404(Post, pk=post_id)

    if not original.active:
        return HttpResponseForbidden("No se puede modificar un post inactivo")

    if (
        not request.user.has_perm(POST_EDIT_PERMISSION)
        and original.author != request.user
    ):
        return HttpResponseForbidden(
            "No tienes permisos para acceder a las versiones de este post"
        )

    # Evitar que un post en estado publicado pueda ser revertido
    if original.status == original.PUBLISHED:
        return HttpResponseForbidden("Un post publicado no puede ser revertido")

    # Que no se pueda hacer reversion durante el proceso de edicion/aprobacion/publicacion
    # a menos que este en "derecho" de realizar dicha modificacion.

    version = get_object_or_404(Version, version=version, post_id=original.id)

    RestorePost(original, version)

    return HttpResponseRedirect(reverse("post_versions", kwargs={"id": post_id}))


@login_required
def post_statistics(request, id):
    """
    Vista para mostrar estadísticas de un post específico.

    Argumentos:
        request: El objeto de solicitud HTTP.
        id: El ID del post para obtener sus estadísticas.

    Retorna:
        Renderiza la página statistics con los registros, versiones y estadísticas de Disqus del post.
        Si el usuario no tiene permisos o no es el autor del post, devuelve un HttpResponseForbidden.
    """
    post = get_object_or_404(Post, pk=id)

    if (
        not request.user.has_perm(POST_REVIEW_PERMISSION)
        and post.author != request.user
    ):
        return HttpResponseForbidden(
            "No tienes permisos para acceder a las estadisticas de este post"
        )

    ctx = new_ctx(
        request,
        {
            "post": post,
            "logs": Log.objects.filter(post=post).order_by("-id")[:5],
            "versions": Version.objects.filter(post_id=post.id).order_by("-id")[:5],
            "disqus": get_disqus_stats(post.id),
        },
    )

    return render(request, "pages/statistics.html", ctx)
