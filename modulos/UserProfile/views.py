from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .decorators import role_required
from .forms import CustomUserCreationForm, UserGroupForm


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    redirect_authenticated_user = True  # Redirect if already logged in

    def get_redirect_url(self):
        # Default redirection
        redirect_to = self.request.POST.get("next", "")

        # FIX: cambiar el url de admin a home
        return redirect_to or reverse_lazy("admin:index")


# Vista para listar usuarios
@login_required
@role_required(allowed_roles=["admin"])  # Solo permitido para el rol 'admin'
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, "admin_panel/user_list.html", {"users": users})


# Vista para editar un usuario existente
@login_required
@role_required(allowed_roles=["admin"])
def user_edit(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_list")
    else:
        form = CustomUserCreationForm(instance=user)
    return render(request, "admin_panel/user_form.html", {"form": form})


# Vista para eliminar un usuario
@login_required
@role_required(allowed_roles=["admin"])
def user_delete(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return render(request, "admin_panel/user_confirm_delete.html", {"user": user})


@login_required
@role_required(allowed_roles=["admin"])
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
