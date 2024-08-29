from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from modulos.Authorization import permissions
from modulos.Authorization.roles import ADMIN

from .decorators import permissions_required
from .forms import CustomUserCreationForm, UserGroupForm
from .models import UserProfile


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_invalid(self, form):
        # Perform the redirection on form failure
        for field, errors in form.errors.items():
            print(f"Campo: {field} - Errores: {errors}")
        return redirect(reverse_lazy("signup"))


class CustomLoginView(LoginView):
    redirect_authenticated_user = True  # Redirect if already logged in

    def get_redirect_url(self):
        # Default redirection
        redirect_to = self.request.POST.get("next", "")

        return redirect_to or reverse_lazy("user_list")


# Vista para listar usuarios
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, "admin_panel/user_list.html", {"users": users})


# Vista para editar un usuario existente
@login_required
# FIX: anadir chequeo de permisos
def user_edit(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            print(form.save())
            return redirect("user_list")
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, "admin_panel/user_form.html", {"form": form})


# Vista para eliminar un usuario
@login_required
# FIX: anadir chequeo de permisos
def user_delete(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return render(request, "admin_panel/user_confirm_delete.html", {"user": user})


@login_required
# FIX: anadir chequeo de permisos
def manage_user_groups(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        form = UserGroupForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect(
                "user_list"
            )  # Redirige al listado de usuarios después de guardar
    else:
        form = UserGroupForm(instance=user)
    return render(
        request, "admin_panel/manage_user_groups.html", {"form": form, "user": user}
    )
