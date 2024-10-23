from modulos.Authorization.permissions import (KANBAN_VIEW_PERMISSION,
                                               VIEW_PURCHASED_CATEGORIES)
from modulos.Categories.models import Category
from modulos.Posts.forms import SearchPostForm


def new_ctx(req, params):
    """
    Creates a wrapper context dictionary for rendering templates, based on user permissions
    and additional parameters. It merges a given custom context passed as parameter with
    the common context for the rest of the pages and views.

    Args:
        req (HttpRequest): The HTTP request object containing user information.
        params (dict): Additional parameters to be included in the context.

    Returns:
        dict: A dictionary containing the context for rendering templates, including user permissions
        and a list of categories.

    Example:
        >>> base = {"form": OurForm, "data": OurData}
        >>> ctx = new_ctx(request, base)
        >>> return render(req, "template", ctx)
    """
    sitios = []
    kanban_permission = False
    finances_permission = False
    if req.user.is_authenticated:
        kanban_permission = req.user.has_perm(KANBAN_VIEW_PERMISSION)
        finances_permission = req.user.has_perm(VIEW_PURCHASED_CATEGORIES)
        # Para poder listar permisos "parecidos", en vez de tener que buscar por permisos especificos.
        # Esto ya que para ver el panel de control solo se necesita saber si se contiene
        # ciertos permisos, no permisos especificos
        permisos = req.user.get_all_permissions()
        for perm in permisos:
            if "user" in perm and perm not in sitios:
                sitios.append("user")
            if "post" in perm and perm not in sitios:
                sitios.append("post")
            if "categor" in perm and perm not in sitios:
                sitios.append("category")
            if "role" in perm and perm not in sitios:
                sitios.append("role")
            if "delete" in perm and perm not in sitios:
                sitios.append("delete")
            if "create" in perm and perm not in sitios:
                sitios.append("create")
            if "edit" in perm and perm not in sitios:
                sitios.append("edit")

    # TODO: listar solo las categorias de interes o las mas votadas capaz
    base = {
        "categories": Category.objects.all(),
        "permisos": sitios,
        "post_search_input": SearchPostForm,
        "has_kanban_access": kanban_permission,
        "has_financial_acces": finances_permission,
    }
    base.update(params)

    return base
