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
from modulos.Pagos.models import Payment


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
        user = request.user

        # Permitir acceso a categorías gratuitas sin autenticación
        if category.tipo == category.GRATIS:
            return super().get(request, *args, **kwargs)

        # Para categorías de suscripción y premium, verificar acceso del usuario
        if user.is_authenticated:
            if not user_has_access_to_category(user, category):
                # Para categorías premium, verificar pago completado
                if category.tipo == category.PREMIUM:
                    if not Payment.objects.filter(
                        user=user, category=category, status="completed"
                    ).exists():
                        return render(
                            request,
                            "access_denied_modal.html",
                            {
                                "category": category,
                                "modal_message": "Para poder ingresar a esta categoría debes suscribirte pagando 1$.",
                            },
                        )
                # Para categorías de suscripción, mostrar mensaje de acceso restringido
                elif category.tipo == category.SUSCRIPCION:
                    return render(
                        request,
                        "access_denied_modal.html",
                        {
                            "category": category,
                            "modal_message": "Para poder ingresar a esta categoría debes ser suscriptor de nuestra web.",
                        },
                    )
                else:
                    return render(
                        request,
                        "access_denied_modal.html",
                        {
                            "category": category,
                            "modal_message": "No tienes acceso a esta categoría.",
                        },
                    )
        else:
            # Usuario no autenticado, mostrar mensaje de acceso restringido para premium o suscripción
            if category.tipo in [category.PREMIUM, category.SUSCRIPCION]:
                return render(
                    request,
                    "access_denied_modal.html",
                    {
                        "category": category,
                        "modal_message": "Para poder ingresar a esta categoría debes iniciar sesión o registrarte.",
                    },
                )

        # Si el usuario tiene acceso, renderizar el detalle de la categoría
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context["posts"] = Post.objects.filter(category=category, status=Post.PUBLISHED)

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
