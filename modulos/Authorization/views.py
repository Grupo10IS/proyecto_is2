from typing import List

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.shortcuts import HttpResponse, get_object_or_404, redirect, render

from modulos.Authorization import permissions
from modulos.Authorization.decorators import permissions_required
from modulos.Authorization.forms import CustomRoleCreationForm
from modulos.Authorization.roles import default_roles
from modulos.utils import new_ctx

# Create your views here.


@login_required
@permissions_required([permissions.ROLE_VIEW_PERMISSION])
def role_information(req, id: int):
    """
    Ver la informacion general del rol con los permisos asignados
    """
    rol = get_object_or_404(Group, id=id)
    return render(req, "authorization/role_details.html", new_ctx(req, {"role": rol}))


@login_required
@permissions_required([permissions.ROLE_VIEW_PERMISSION])
def role_list(req):
    """
    View para listar los roles existentes en el sistema
    """
    roles = Group.objects.all()
    return render(
        req,
        "authorization/role_list.html",
        new_ctx(req, {"roles": roles, "default_roles": default_roles}),
    )


@login_required
@permissions_required([permissions.ROLE_MANAGE_PERMISSION])
def role_delete(req, id: int):
    """
    View para eliminar un sistema rol del sistema
    """
    role = Group.objects.get(id=id)
    try:
        role.delete()
        return redirect("role_list")
    except:
        return HttpResponse("No se ha encontrado el rol")


@login_required
@permissions_required([permissions.ROLE_MANAGE_PERMISSION])
def role_create(request):
    """
    View form crear un nuevo rol del sistema
    """
    if request.method == "POST":
        form = CustomRoleCreationForm(request.POST)
        if form.is_valid():
            perms: List[str] | None = form.cleaned_data.get("perms")
            if perms == None or len(perms) == 0:
                return HttpResponse("Debe proporcionar los permisos")

            new_role = form.save(commit=False)
            new_role.save()

            # asignar permisos
            for perm in perms:
                p = Permission.objects.get(codename=perm)
                if p:
                    new_role.permissions.add(p)

            new_role.save()
            return redirect("role_list")

    return render(
        request,
        "authorization/role_form.html",
        new_ctx(request, {"form": CustomRoleCreationForm()}),
    )
