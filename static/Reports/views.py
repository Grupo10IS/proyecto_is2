from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, render

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import VIEW_REPORTS
from modulos.Posts.models import Post
from modulos.Reports.forms import ReportForm
from modulos.Reports.models import Report
from modulos.utils import new_ctx


@login_required
def create_report(request, id):
    """
    Crea un nuevo reporte asociado a un post específico.

    Parámetros:
    - request: El objeto HttpRequest que contiene la información de la petición.
    - id: El ID del post al que se le va a asociar el reporte.

    Retorno:
    - JsonResponse indicando el éxito o fracaso de la operación.
    - Si el método es GET, renderiza el formulario de creación de reportes.
    """
    post = get_object_or_404(Post, id=id)
    existing_report = Report.objects.filter(content=post, user=request.user).first()

    if existing_report:
        return JsonResponse(
            {"success": False, "message": "Ya has reportado este contenido."},
            status=400,
        )

    if request.method == "POST":
        form = ReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.content = post
            report.user = request.user
            report.save()
            return JsonResponse({"success": True})

        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ReportForm()
        ctx = new_ctx(request, {"post": post, "form": form})

        return render(request, "create_report.html", context=ctx)


@login_required
@permissions_required([VIEW_REPORTS])
def manage_reports(request):
    """
    Muestra una lista de posts que tienen reportes asociados.

    Parámetros:
    - request: El objeto HttpRequest que contiene la información de la petición.

    Retorno:
    - Renderiza una plantilla con los posts que tienen reportes y los permisos del usuario.
    """
    posts_with_reports = Post.objects.annotate(
        report_count=Count("reports", filter=Q(reports__is_handled=False))
    ).filter(report_count__gt=0)

    permisos = request.user.get_all_permissions()
    perm_view_reports = "UserProfile." + VIEW_REPORTS in permisos

    ctx = new_ctx(
        request,
        {
            "posts_with_reports": posts_with_reports,
            "perm_view_reports": perm_view_reports,
        },
    )

    return render(request, "report_list.html", ctx)


@login_required
@permissions_required([VIEW_REPORTS])
def report_detail(request, id):
    """
    Muestra los reportes asociados a un post específico.

    Parámetros:
    - request: El objeto HttpRequest que contiene la información de la petición.
    - id: El ID del post reportado.

    Retorno:
    - Renderiza una plantilla con los reportes del post y su título.
    """
    post = get_object_or_404(Post, id=id)
    reports = Report.objects.filter(content=post)

    content_title = (
        reports.first().content.title if reports else "Contenido no encontrado"
    )

    permisos = request.user.get_all_permissions()
    perm_view_reports = "UserProfile." + VIEW_REPORTS in permisos

    ctx = new_ctx(
        request,
        {
            "reports": reports,
            "content_title": content_title,
            "perm_view_reports": perm_view_reports,
        },
    )

    return render(request, "content_report_list.html", ctx)


@login_required
@permissions_required([VIEW_REPORTS])
def review(request, id):
    """
    Envía un post a revisión.

    Parámetros:
    - request: El objeto HttpRequest que contiene la información de la petición.
    - id: El ID del post a enviar a revisión.

    Retorno:
    - Renderiza la plantilla con los posts que tienen reportes.
    """
    post = get_object_or_404(Post, id=id)

    post.status = Post.PENDING_REVIEW
    post.save()

    # Actualiza is_handled a True para todos los reportes relacionados con el post
    post.reports.update(is_handled=True)

    # Retorna solo los posts no tratados
    posts_with_reports = Post.objects.annotate(
        report_count=Count("reports", filter=Q(reports__is_handled=False))
    ).filter(report_count__gt=0)

    ctx = new_ctx(request, {"posts_with_reports": posts_with_reports})

    return render(request, "report_list.html", ctx)
