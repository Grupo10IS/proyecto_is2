from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"  # Default home for non-admin users

    def get(self, request, *args, **kwargs):
        # Verificar si el usuario pertenece al grupo "Administrador"
        if request.user.groups.filter(name="Administrador").exists():
            # Redirigir al home personalizado para administradores
            return redirect(reverse("admin_home"))
        return super().get(request, *args, **kwargs)


class AdminHomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home_for_admin.html"
