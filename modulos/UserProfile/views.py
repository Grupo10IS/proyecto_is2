from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView
from modulos.Authorization import permissions

from .decorators import permissions_required
from .forms import (CustomUserChangeForm, CustomUserCreationForm, ProfileForm,
                    UserGroupForm)
from .models import UserProfile


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_invalid(self, form):
        # Limpiar los textos de ayuda predeterminados si el formulario es inválido
        if form.has_error("password1"):
            form.fields["password1"].help_text = (
                ""  # Elimina el texto de ayuda predeterminado para el campo password1
            )
        if form.has_error("password2"):
            form.fields["password2"].help_text = (
                ""  # Elimina el texto de ayuda predeterminado para el campo password2
            )

        return self.render_to_response(self.get_context_data(form=form))


class CustomLoginView(LoginView):
    redirect_authenticated_user = True  # Redirigir si ya está autenticado

    def get_redirect_url(self):
        # Default redirection
        redirect_to = self.request.POST.get("next", "")
        return redirect_to or reverse_lazy("home")

    def form_invalid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")

        # Verifica si el usuario existe
        if not UserProfile.objects.filter(username=username).exists():
            messages.error(self.request, "Usuario incorrecto o no existe")
        else:
            # Verifica la contraseña
            user = authenticate(self.request, username=username, password=password)
            if user is None:
                messages.error(self.request, "Contraseña Incorrecta")

        return self.render_to_response(self.get_context_data(form=form))


@login_required
def profile_view(request):
    if request.method == "POST":
        u_form = CustomUserChangeForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile")
    else:
        u_form = CustomUserChangeForm(instance=request.user)
        p_form = ProfileForm(instance=request.user)

    context = {
        "u_form": u_form,
        "p_form": p_form,
        "groups": request.user.groups.all(),
    }

    return render(request, "registration/profile.html", context)


# Vista para listar usuarios
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_list(request):
    users = UserProfile.objects.all()
    return render(request, "admin_panel/user_list.html", {"users": users})


# Vista para editar un usuario existente
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
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
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_delete(request, user_id):
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")
    return render(request, "admin_panel/user_confirm_delete.html", {"user": user})

# Vista para agregar un rol a un usuario
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
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
