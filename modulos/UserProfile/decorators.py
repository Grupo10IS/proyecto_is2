from django.http import HttpResponseForbidden


def permissions_required(perms: list[str]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            for p in perms: 
                if not request.user.has_perm(p):
                    return HttpResponseForbidden(
                        "No tienes permiso para acceder a esta página."
                    )
                return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
