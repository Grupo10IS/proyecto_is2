from django.http import HttpResponseForbidden


def permissions_required(perms: list[str]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Verificar que el usuario tenga todos los permisos requeridos
            has_all_perms = all(request.user.has_perm("Categories." + p) for p in perms)
            if not has_all_perms:
                return HttpResponseForbidden(
                    "No tienes permiso para acceder a esta página."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
