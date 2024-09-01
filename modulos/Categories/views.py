from multiprocessing import context
from pyexpat.errors import messages
from django.views import generic
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from modulos.Authorization import permissions
from modulos.Categories.forms import CategoryCreationForm
from modulos.Categories.decorators import permissions_required
from modulos.Categories.models import Category
from modulos.Posts.models import Post


class CategoryCreateView(generic.CreateView):
    form_class = CategoryCreationForm
    template_name = "create_category.html"
    success_url = "/categories/"


# Vista para crear categorias
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_create(request):
    if request.method == "POST":
        form = CategoryCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryCreationForm()
    context = {"form": form}
    return render(request, "category_form.html", context)


# Vista para listar categorias
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_list(request):
    categories = Category.objects.all()
    return render(request, "category_list.html", {"categories": categories})


# Vista para eliminar una categoría
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        # Verifica si hay posts asociados a esta categoría
        if Post.objects.filter(category=category).exists():
            # Mostrar un mensaje de error si hay posts asociados
            return render(
                request,
                "category_confirm_delete.html",
                {
                    "category": category,
                    "error_message": "No se puede eliminar la categoría porque tiene posts asociados.",
                },
            )

        # Elimina la categoría si no hay posts asociados
        category.delete()
        return redirect("category_list")
    return render(request, "category_confirm_delete.html", {"category": category})


# Vista para editar un usuario existente
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        form = CategoryCreationForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("category_list")
    else:
        form = CategoryCreationForm(instance=category)
    return render(request, "category_form.html", {"form": form})
