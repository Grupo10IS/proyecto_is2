from django.urls import path

from .views import *

urlpatterns = [
    path("", manage_post, name="post_list"),
    path("list/", list_contenidos_view, name="list_contenidos"),
    path("<int:id>/", view_post, name="post_detail"),
    path("create/", create_post, name="post_create"),
    path("<int:id>/delete", delete_post, name="delete_post"),
    path("<int:id>/edit/", edit_post, name="edit_post"),
    path("search/", search_post, name="post_search"),
    # -- vistas de publicacion de contenido --
    path("<int:id>/approve", aprove_post, name="approve_post"),
    path("<int:id>/review", send_to_review, name="send_to_review"),
    path("<int:id>/publish", publish_post, name="publish_post"),
    path("<int:id>/reject", reject_post, name="reject_post"),
    path("kanban/", kanban_board, name="kanban_board"),
    # -- historial y estadisticas
    path("<int:id>/versions", post_versions_list, name="post_versions"),
    path(
        "<int:post_id>/versions/<int:version>/",
        post_version_detail,
        name="post_version_detail",
    ),
    path("<int:id>/logs", post_log_list, name="post_log_list"),
    # -- miscelanea --
    path("<int:id>", favorite_post, name="post_favorite"),
    path("favorites", favorite_list, name="post_favorite_list"),
]
