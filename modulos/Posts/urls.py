from django.urls import path
from .views import PostDetailView

urlpatterns = [
    path("post/<int:pk>/", PostDetailView.as_view(), name="post_detail"),
]
