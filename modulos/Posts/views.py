from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from modulos.Categories.models import Category  # Importa el modelo de categorías
from django.views.generic import DetailView
from .models import Post
from django.contrib.auth.decorators import login_required
from .decorators import permissions_required
from modulos.Authorization import permissions

class HomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home.html"  # Default home for non-admin users

    @permissions_required([permissions.USERS_VIEW_ALL_PROFILES_PERMISSION])
    def get(self, request, *args, **kwargs):
        return redirect(reverse("admin_home"))

    # Añade todas las categorías al home
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class AdminHomeView(LoginRequiredMixin, TemplateView):
    template_name = "pages/home_for_admin.html"

    # Añade todas las categorías al home del admin
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"
