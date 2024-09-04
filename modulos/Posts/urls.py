from django.urls import path

from .views import create_post, view_post

urlpatterns = [
    path("<int:id>/", view_post, name="post_detail"),
    path("create/", create_post, name="post_create"),
]
