from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views import generic
from django.views.generic import DetailView, ListView
from modulos.Authorization.permissions import user_has_access_to_category
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


# views.py de categories

class CategoryListView(ListView):
    model = Category
    template_name = "categories_list.html"  # Plantilla por defecto
    context_object_name = "categories"

    def get_queryset(self):
        queryset = super().get_queryset()
        # Verificar si se pasó el parámetro 'premium' en la URL
        premium_only = self.request.GET.get("premium", "false").lower() == "true"

        # Filtrar categorías por tipo PREMIUM si el parámetro es true
        if premium_only:
            queryset = queryset.filter(tipo=Category.PREMIUM)
        return queryset

    def get_template_names(self):
        # Cambiar a la plantilla 'categories_premium.html' si el parámetro 'premium' es true
        premium_only = self.request.GET.get("premium", "false").lower() == "true"
        if premium_only:
            return ["categories_premium.html"]
        return ["categories_list.html"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return new_ctx(self.request, context)


class CategoryDetailView(DetailView):
    model = Category
    template_name = "category_detail.html"
    context_object_name = "category"

    def get(self, request, *args, **kwargs):
        category = self.get_object()

        # Check if the user has access to this category
        if not user_has_access_to_category(request.user, category):
            # If the category is 'Suscripcion', show the subscription modal
            if category.tipo == category.SUSCRIPCION:
                return render(
                    request,
                    "access_denied_modal.html",
                    {
                        "category": category,
                        "modal_message": "Para poder ingresar a esta categoría debes ser suscriptor de nuestra web. Por favor, inicia sesión o crea una cuenta.",
                    },
                )
            # If the category is 'Premium', check if the user is logged in
            elif category.tipo == category.PREMIUM:
                if request.user.is_authenticated:
                    # If the user is logged in but doesn't have access, show payment option
                    return render(
                        request,
                        "access_denied_modal.html",
                        {
                            "category": category,
                            "modal_message": "Para poder ingresar a esta categoría debes de suscribirte pagando 1$.",
                        },
                    )
                else:
                    # If the user is not logged in, prompt them to log in or sign up
                    return render(
                        request,
                        "access_denied_modal.html",
                        {
                            "category": category,
                            "modal_message": "Debes iniciar sesión o registrarte para poder suscribirte a esta categoría premium.",
                        },
                    )

        # If the user has access, proceed with the normal detail view
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Add related posts to the context
        category = self.get_object()
        context["posts"] = Post.objects.filter(category=category)
        return new_ctx(self.request, context)


# Vista para crear categorias
@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def category_create(request):
    if request.method == "POST":
        form = CategoryCreationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("category_list")
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
    return render(request, "category_list.html", ctx)


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
        return redirect("category_list")

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
                form.cleaned_data["status"] == "INACTIVO"
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
            return redirect("category_list")

    form = CategoryCreationForm(instance=category)
    return render(request, "category_form.html", new_ctx(request, {"form": form}))
