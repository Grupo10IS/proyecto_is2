from modulos.Categories.models import Category


def new_ctx(req, params):
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
    }
    base.update(params)

    return base
