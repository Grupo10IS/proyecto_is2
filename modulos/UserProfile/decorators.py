from django.http import HttpResponseForbidden


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden(
                    "No tienes permiso para acceder a esta página."
                )
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
