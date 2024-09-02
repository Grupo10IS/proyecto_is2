from django.urls import path

from modulos.Categories.views import *


urlpatterns = [
    path("", category_list, name="category_list"),
    path("list/", CategoryListView.as_view(), name="categories_list"),
    path("<int:pk>/", CategoryDetailView.as_view(), name="category_detail"),
    path("category_create/", category_create, name="category_create"),
    path("category_delete/<int:category_id>/", category_delete, name="category_delete"),
    path("category_edit/<int:category_id>/", category_edit, name="category_edit"),
]
