from django.contrib.auth.decorators import login_required
from django.db.models import Count, OuterRef, Subquery
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from pyexpat.errors import messages

from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.permissions import VIEW_REPORTS
from modulos.Posts.models import Post
from modulos.Reports.forms import ReportForm
from modulos.Reports.models import Report
from modulos.utils import new_ctx


@login_required
def create_report(request, id):
    # Obtenemos el post al que se va a asociar el reporte
    post = get_object_or_404(Post, id=id)
    # Limitar a un reporte por usuario por contenido
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
            return JsonResponse({"success": True})  # Respuesta JSON indicando éxito

        # Si el formulario no es válido, podrías retornar errores aquí si deseas
        return JsonResponse({"success": False, "errors": form.errors}, status=400)
    else:
        form = ReportForm()
        ctx = new_ctx(request, {"post": post, "form": form})
        return render(request, "create_report.html", context=ctx)


# Vista para listar contenidos reportados
"""@login_required
@permissions_required([VIEW_REPORTS])
def manage_reports(request):
    reports = Report.objects.all().distinct()
    permisos = request.user.get_all_permissions()

    # Definición de permisos en variables booleanas
    perm_view_reports = "UserProfile." + VIEW_REPORTS in permisos

    # Cantidad de reportes por post

    # Definición de contexto basado en permisos
    ctx = new_ctx(
        request,
        {
            "reports": reports,
            "perm_view_reports": perm_view_reports,
        },
    )

    return render(request, "report_list.html", ctx)
"""


@login_required
@permissions_required([VIEW_REPORTS])
def manage_reports(request):
    # Obtener los posts que tienen reportes y contar cuántos reportes tiene cada uno
    posts_with_reports = Post.objects.annotate(report_count=Count("reports")).filter(
        report_count__gt=0
    )

    permisos = request.user.get_all_permissions()

    # Definición de permisos en variables booleanas
    perm_view_reports = "UserProfile." + VIEW_REPORTS in permisos

    # Definición de contexto basado en permisos
    ctx = new_ctx(
        request,
        {
            "posts_with_reports": posts_with_reports,
            "perm_view_reports": perm_view_reports,
        },
    )

    return render(request, "report_list.html", ctx)


# Vista para listar reportes por contenido
@login_required
@permissions_required([VIEW_REPORTS])
def report_detail(request, id):
    # Obtenemos el post reportado
    post = get_object_or_404(Post, id=id)
    # Obtenemos todos los reportes de contenido
    reports = Report.objects.filter(content=post)

    content_title = reports.first().content.title

    permisos = request.user.get_all_permissions()

    # Definición de permisos en variables booleanas
    perm_view_reports = "UserProfile." + VIEW_REPORTS in permisos

    # Definición de contexto basado en permisos
    ctx = new_ctx(
        request,
        {
            "reports": reports,
            "content_title": content_title,
            "perm_view_reports": perm_view_reports,
        },
    )

    return render(request, "content_report_list.html", ctx)
