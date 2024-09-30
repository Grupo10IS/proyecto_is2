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
    # -- vistas de publicacion de contenido --
    path("approve/<int:id>/", aprove_post, name="approve_post"),
    path("review/<int:id>/", send_to_review, name="send_to_review"),
    path("posts/publish/<int:id>/", publish_post, name="publish_post"),
    path("posts/reject/<int:id>/", reject_post, name="reject_post"),
    path("kanban/", kanban_board, name="kanban_board"),
    # -- estadisticas --
    path("<int:id>", favorite_post, name="post_favorite"),
    path("favorites", favorite_list, name="post_favorite_list"),
]
