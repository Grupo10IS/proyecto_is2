from django.http import HttpResponseForbidden


def permissions_required(perms: list[str]):
    """
    Decorador para verificar que el usuario tenga los permisos especificados.

    Este decorador recibe una lista de permisos y verifica si el usuario autenticado tiene
    cada uno de ellos. Si el usuario no tiene alguno de los permisos requeridos, se devuelve
    una respuesta de `HttpResponseForbidden`. Si el usuario tiene todos los permisos,
    la vista original se ejecuta normalmente.

    Args:
        perms (list[str]): Lista de permisos que se deben verificar. Cada permiso debe ser
        una cadena con el nombre del permiso (sin prefijo de aplicación).

    Returns:
        function: Una vista envuelta que verifica los permisos antes de ejecutar la vista original.

    Ejemplo:
        @permissions_required(["can_edit", "can_delete"])
        def my_view(request):
            # Vista lógica aquí
    """

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if any(request.user.has_perm("UserProfile." + p) for p in perms):
                # TODO: redireccionar a una pagina linda
                return view_func(request, *args, **kwargs)

            return HttpResponseForbidden(
                "No tienes permiso para acceder a esta página."
            )

        return _wrapped_view

    return decorator
