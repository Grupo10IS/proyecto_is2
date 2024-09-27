import difflib
import logging
from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.http.response import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import (KANBAN_VIEW_PERMISSION,
                                               POST_APPROVE_PERMISSION,
                                               POST_CREATE_PERMISSION,
                                               POST_DELETE_PERMISSION,
                                               POST_EDIT_PERMISSION,
                                               POST_PUBLISH_PERMISSION,
                                               POST_REJECT_PERMISSION,
                                               POST_REVIEW_PERMISSION)
from modulos.Authorization.roles import ADMIN
from modulos.Categories.models import Category
from modulos.Posts.buscador import buscador
from modulos.Posts.forms import NewPostForm, SearchPostForm
from modulos.Posts.models import Log, NewVersion, Post, Version
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

    ctx = new_ctx(req, {"posts": Post.objects.filter(status=Post.PUBLISHED)[:10]})

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

    # Permitir ver la publicación solo si está publicada o si el usuario es el autor o tiene permisos
    if (
        post.status != Post.PUBLISHED
        and post.author != request.user
        and not request.user.has_perm(POST_REVIEW_PERMISSION)
    ):
        return HttpResponseBadRequest("No tienes permiso para ver esta publicación.")

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
        form = NewPostForm(request.POST, request.FILES)
        if not form.is_valid():
            return HttpResponseBadRequest("Datos proporcionados invalidos")

        p = form.save(commit=False)
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


# Vista para eliminar un post
@login_required
def delete_post(request, id):
    post: Post = get_object_or_404(Post, pk=id)
    if not request.user.has_perm(POST_DELETE_PERMISSION) or post.author != request.user:
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
    Cuando se realiza una modificacion de un post y el mismo se encuentra en cualquier estado
    que no sea borrador, entonces se guarda una version del estado anterior del post a modo de historial de
    cambios.
    """
    post = get_object_or_404(Post, pk=id)

    if request.method == "POST":
        version = NewVersion(post)

        form = NewPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            form.save()
            post.version += 1
            post.save()

            # Guardar la revisión solo si el post no es un borrador
            if post.status != Post.DRAFT:
                version.save()

            return redirect("post_list")
        else:
            print(f"Formulario inválido")

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
    # FIX: generar revision cuando se realiza un rechazo, ademas de hacer una suerte de form
    # para poder anadir comentarios al rechazo.
    return redirect("kanban_board")


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

    if not request.user.has_perm(POST_REVIEW_PERMISSION) or original.author != request.user:
        return HttpResponseForbidden("No tienes permisos para acceder a las versiones de este post")

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
def post_log_list(request, id):
    post = get_object_or_404(Post, pk=id)

    if not request.user.has_perm(POST_REVIEW_PERMISSION) or post.author != request.user:
        return HttpResponseForbidden("No tienes permisos para acceder a los logs de este post")

    logs = Log.objects.filter(post=post).order_by("-creation_date")

    return render(request, "pages/logs_list.html", new_ctx(request, {"logs": logs}))
