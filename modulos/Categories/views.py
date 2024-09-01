from multiprocessing import context
from pyexpat.errors import messages
from django.views import generic
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from modulos.Authorization import permissions
from modulos.Categories.forms import CategoryCreationForm
from modulos.Categories.decorators import permissions_required


class CategoryCreateView(generic.CreateView):
    form_class = CategoryCreationForm
    template_name = "create_category.html"
    success_url = "/categories/category_create/"


@login_required
@permissions_required([permissions.CATEGORY_MANAGE_PERMISSION])
def create_category(request):
    if request.method == "POST":
        form = CategoryCreationForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = CategoryCreationForm()
    context = {"form": form}
    return render(request, "create_category.html", context)
