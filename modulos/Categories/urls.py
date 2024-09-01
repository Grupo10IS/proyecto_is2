from django.urls import path

from modulos.Categories.views import create_category


urlpatterns = [
    path("category_create/", create_category, name="category_create"),
]
