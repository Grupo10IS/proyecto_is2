from django.urls import path

from .views import *

urlpatterns = [
    path("", manage_post, name="post_list"),
    path("<int:id>/", view_post, name="post_detail"),
    path("create/", create_post, name="post_create"),
    path("delete/<int:id>/", delete_post, name="delete_post"),
    # path("category_edit/<int:category_id>/", category_edit, name="category_edit"),
]
