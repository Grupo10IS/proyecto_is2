from django.urls import path
from .views import *

urlpatterns = [
    path("", manage_post, name="post_list"),
    path("list/", ContenidosView.as_view(), name="contenidos"),
    path("<int:id>/", view_post, name="post_detail"),
    path("create/", create_post, name="post_create"),
    path("delete/<int:id>/", delete_post, name="delete_post"),
    path("edit/<int:id>/", edit_post, name="edit_post"),
    path("search", search_post, name="post_search"),
]
