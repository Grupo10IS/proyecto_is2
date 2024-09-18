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

    # TODO: listar solo las categorias de interes o las mas votadas capaz
    base = {
        "categories": Category.objects.all(),
        "permisos": sitios,
        "post_search_input": SearchPostForm
    }
    base.update(params)

    return base
