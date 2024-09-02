from django.shortcuts import render
from django.views.generic import DetailView

from modulos.Categories.models import Category
from modulos.Posts.models import Post


def home_view(req):
    sitios = []
    if req.user.is_authenticated:
        permisos = req.user.get_all_permissions()

        # Itera sobre los permisos
        for perm in permisos:
            if "user" in perm and perm not in sitios:
                sitios.append("user")
            if "post" in perm and perm not in sitios:
                sitios.append("post")
            if "categor" in perm and perm not in sitios:
                sitios.append("category")
            if "role" in perm and perm not in sitios:
                sitios.append("role")

    return render(
        req,
        "pages/home.html",
        context={
            "categories": Category.objects.all(),
            "sitios": sitios,
        },
    )


class PostDetailView(DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"
