from django.contrib.auth.decorators import login_required
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views import generic
from django.views.generic import DetailView, ListView

from modulos.Authorization import permissions
from modulos.Authorization.decorators import permissions_required
from modulos.Categories.forms import CategoryCreationForm
from modulos.Categories.models import Category
from modulos.Posts.models import Post
from modulos.utils import new_ctx


class CategoryCreateView(generic.CreateView):
    form_class = CategoryCreationForm
    template_name = "create_category.html"
    success_url = "/categories/"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar más contexto
        return new_ctx(self.request, context)


class CategoryListView(ListView):
    model = Category
    template_name = "categories_list.html"  # Plantilla por defecto
    context_object_name = "categories"

    def get_template_names(self):
        # Cambiar a la plantilla 'categories_premium.html' si el parámetro 'premium' es true
        return ["categories_list.html"]

class CategoryDetailView(DetailView):
    model = Category
    template_name = "category_detail.html"
    context_object_name = "category"

    def get(self, request, *args, **kwargs):
        # Permitir acceso a categorías gratuitas sin autenticación
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        request = self.request
        context = super().get_context_data(**kwargs)
        category = self.get_object()

        try:
            page = int(request.GET.get("page", 1))
        except ValueError:
            page = 1

        if page <= 0:
            page = 1

        # Filtrar solo los posts activos, publicados y no expirados en la categoría
        posts = Post.objects.filter(
            active=True,
            status=Post.PUBLISHED,
            category=category,
        ).filter(
            Q(expiration_date__gt=timezone.now()) | Q(expiration_date__isnull=True)
        )[
            20 * (page - 1) : 20 * page
        ]

        context["posts"] = posts

        if len(posts) >= 20:
            context["next_page"] = page + 1

        if page > 1:
            context["previous_page"] = page - 1

        return new_ctx(self.request, context)


# Vista para crear categorias
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_create(request):
    if request.method == "POST":
        form = CategoryCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("category_admin")
    else:
        form = CategoryCreationForm()

    context = new_ctx(request, {"form": form})

    return render(request, "category_form.html", context)


# Vista para listar categorias
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def categories_manage(request):
    categories = Category.objects.all()
    ctx = new_ctx(request, {"categories": categories})
    return render(request, "category_admin.html", ctx)


# Vista para eliminar una categoría
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        # Verifica si hay posts asociados a esta categoría
        if Post.objects.filter(category=category).exists():
            # Mostrar un mensaje de error si hay posts asociados
            ctx = new_ctx(
                request,
                {
                    "category": category,
                    "error_message": "No se puede eliminar la categoría porque tiene posts asociados.",
                },
            )
            return render(
                request,
                "category_confirm_delete.html",
                ctx,
            )

        # Elimina la categoría si no hay posts asociados
        category.delete()
        return redirect("category_admin")

    ctx = new_ctx(request, {"category": category})
    return render(request, "category_confirm_delete.html", ctx)


# Vista para editar una categoria existente
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == "POST":
        form = CategoryCreationForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            # Verifica si la categoría está siendo cambiada a inactiva y tiene posts asociados
            if (
                form.cleaned_data["status"] == "Inactivo"
                and Post.objects.filter(category=category).exists()
            ):
                return render(
                    request,
                    "category_form.html",
                    new_ctx(
                        request,
                        {
                            "form": form,
                            "error_message": "No se puede inactivar la categoría porque tiene posts asociados.",
                        },
                    ),
                )
            form.save()

            return redirect("category_admin")

    form = CategoryCreationForm(instance=category)
    return render(request, "category_form.html", new_ctx(request, {"form": form}))
