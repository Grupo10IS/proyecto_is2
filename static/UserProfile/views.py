from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http.response import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import generic

from modulos.Authorization import permissions
from modulos.Authorization.decorators import permissions_required
from modulos.utils import new_ctx

from .forms import (CustomUserChangeForm, CustomUserCreationForm,
                    CustomUserEditForm, ProfileForm, UserGroupForm)
from .models import UserProfile


class SignUpView(generic.CreateView):
    """
    Vista de registro 'SignUpView'.

    Permite que los nuevos usuarios se registren creando una cuenta.
    Si el formulario es inválido, elimina los textos de ayuda predeterminados para las contraseñas.

    Attributes:
        form_class (ModelForm): Formulario utilizado para la creación de usuarios (CustomUserCreationForm).
        success_url (str): URL de redirección al iniciar sesión después del registro.
        template_name (str): Plantilla utilizada para renderizar el formulario de registro.
    """

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
    """
    Vista personalizada de inicio de sesión 'CustomLoginView'.

    Gestiona el inicio de sesión de los usuarios. Redirige a la página de inicio si el usuario ya está autenticado.
    Si el formulario es inválido, verifica si el usuario existe y si la contraseña es correcta.

    Attributes:
        redirect_authenticated_user (bool): Si es True, redirige a los usuarios autenticados.
    """

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
    """
    Vista de perfil de usuario 'profile_view'.

    Permite a los usuarios autenticados ver y editar su perfil.
    Gestiona los formularios de actualización de datos del usuario y de su perfil.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido renderizado de la plantilla 'registration/profile.html'.
    """
    # No es necesario usar user_profile = request.user.userprofile
    user_profile = request.user

    if request.method == "POST":
        u_form = CustomUserChangeForm(request.POST, instance=request.user)
        p_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect("profile")  # Redirige a la misma página después de guardar
    else:
        u_form = CustomUserChangeForm(instance=request.user)
        p_form = ProfileForm(instance=user_profile)

    context = new_ctx(
        request,
        {
            "u_form": u_form,
            "p_form": p_form,
            "groups": request.user.groups.all(),
            "user": request.user,
        },
    )

    return render(request, "registration/profile.html", context)


# Vista para listar usuarios
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_list(request):
    """
    Vista para listar usuarios 'user_list'.

    Muestra una lista de todos los usuarios excluyendo al usuario autenticado.
    Requiere autenticación y permisos para ver todos los perfiles de usuario.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.

    Returns:
        HttpResponse: Respuesta HTTP con el contenido renderizado de la plantilla 'admin_panel/user_list.html'.
    """
    users = UserProfile.objects.exclude(id=request.user.id)
    return render(
        request, "admin_panel/user_list.html", new_ctx(request, {"users": users})
    )


# Vista para editar un usuario existente
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_edit(request, user_id):
    """
    Vista para editar un usuario existente 'user_edit'.
    Permite editar la información de un usuario seleccionado.
    Requiere autenticación y permisos para ver todos los perfiles de usuario.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        user_id (int): ID del usuario a editar.

    Returns:
        HttpResponse: Respuesta HTTP con el formulario de edición del usuario.
    """
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("user_list")
        else:
            print(form.errors)  # Imprimir los errores del formulario si no es válido
    else:
        form = CustomUserEditForm(instance=user)

    return render(
        request, "admin_panel/user_form.html", new_ctx(request, {"form": form})
    )


# Vista para eliminar un usuario
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def user_delete(request, user_id):
    """
    Vista para eliminar un usuario 'user_delete'.

    Permite eliminar un usuario específico.
    Requiere autenticación y permisos para ver todos los perfiles de usuario.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        user_id (int): ID del usuario a eliminar.

    Returns:
        HttpResponse: Respuesta HTTP para confirmar o realizar la eliminación.
    """
    user = get_object_or_404(UserProfile, pk=user_id)
    if request.method == "POST":
        user.delete()
        return redirect("user_list")

    return render(
        request,
        "admin_panel/user_confirm_delete.html",
        new_ctx(request, {"user": user}),
    )


# Vista para agregar un rol a un usuario
@login_required
@permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
def manage_user_groups(request, user_id):
    """
    Vista para gestionar roles de un usuario 'manage_user_groups'.

    Permite agregar o eliminar roles de un usuario específico.
    Requiere autenticación y permisos para ver todos los perfiles de usuario.

    Args:
        request (HttpRequest): El objeto de solicitud HTTP.
        user_id (int): ID del usuario al que se le gestionarán los roles.

    Returns:
        HttpResponse: Respuesta HTTP con el formulario de gestión de roles del usuario.
    """
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
        request,
        "admin_panel/manage_user_groups.html",
        new_ctx(request, {"form": form, "user": user}),
    )
