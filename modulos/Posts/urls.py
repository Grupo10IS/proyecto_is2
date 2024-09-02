from django.urls import path
from .views import PostDetailView
from modulos.Posts.views import HomeView

urlpatterns = [
    path("post/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
]
