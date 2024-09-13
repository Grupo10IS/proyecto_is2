import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from modulos.Authorization.permissions import *
from modulos.Categories.models import Category
from modulos.Posts.models import Post


@pytest.mark.django_db
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_home_view(client):
    """
    Test the home view to check if posts are displayed correctly.
    """
    url = reverse("home")

    # Test home view with no posts
    response = client.get(url)
    assert response.status_code == 200
    assert "pages/home.html" in [t.name for t in response.templates]
    assert "posts" in response.context
    assert len(response.context["posts"]) == 0

    # Test home view with existing posts
    Post.objects.create(title="Test Post 1", content="Content of test post 1")
    Post.objects.create(title="Test Post 2", content="Content of test post 2")

    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["posts"]) == 2


@pytest.mark.django_db
def test_view_post(client):
    """
    Test the post detail view with an existing post and a non-existent post.
    """
    post = Post.objects.create(
        title="Test Post", content="Content of test post", tags="tag1, tag2"
    )

    # Test post detail view with an existing post
    url = reverse("post_detail", args=[post.id])
    response = client.get(url)
    assert response.status_code == 200
    assert "pages/post_detail.html" in [t.name for t in response.templates]
    assert response.context["post"] == post
    assert response.context["tags"] == ["tag1", "tag2"]
    assert "categories" in response.context

    # Test post detail view with a non-existent post
    url = reverse("post_detail", args=[999])
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_create_post_view(client):
    """
    Test the create post view for different user permissions and form validation.
    """
    url = reverse("post_create")

    # Test access to create post view without login
    response = client.get(url)
    assert (
        response.status_code == 302
    ), "Should redirect to login page when not logged in."

    # Create user and log in
    user = get_user_model().objects.create_user(
        username="testuser", password="password"
    )
    client.login(username="testuser", password="password")

    # Test access to create post view without permission
    response = client.get(url)
    assert (
        response.status_code == 403
    ), "User without permission should get 403 Forbidden."

    # Assign permission and test access
    user.user_permissions.add(Permission.objects.get(codename=POST_CREATE_PERMISSION))
    response = client.get(url)
    assert (
        response.status_code == 200
    ), "User with permission should access the view successfully."
    assert "pages/new_post.html" in [
        t.name for t in response.templates
    ], "Template 'new_post.html' should be used."

    # Test creating a post with invalid data
    data = {"title": "New Test Post", "content": "Content for new test post"}
    response = client.post(url, data)
    assert (
        response.status_code == 400
    ), "Invalid form data should return 400 Bad Request."

    # Test creating a post with valid data
    category = Category.objects.create(name="test_category", description="descripcion")
    data = {
        "title": "New Test Post",
        "content": "Content for new test post",
        "category": category.id,
    }
    response = client.post(url, data)
    assert response.status_code == 302, "Successful post creation should redirect."

    # test of existing new post
    assert Post.objects.filter(
        title="New Test Post"
    ).exists(), "Post should exist in the database after creation."


@pytest.mark.django_db
def test_post_manage_view(client):
    """
    Test the create post view for different user permissions and form validation.
    """
    url = reverse("post_list")

    # Test access to create post view without login
    response = client.get(url)
    assert (
        response.status_code == 302
    ), "Should redirect to login page when not logged in."

    # Create user and log in
    user = get_user_model().objects.create_user(
        username="testuser", password="password"
    )
    client.login(username="testuser", password="password")

    # Test access to create post view without permission
    response = client.get(url)
    assert (
        response.status_code == 403
    ), "User without permission should get 403 Forbidden."

    # Assign permission and test access
    user.user_permissions.add(Permission.objects.get(codename=POST_CREATE_PERMISSION))
    response = client.get(url)
    assert (
        response.status_code == 200
    ), "User with permission should access the view successfully."
    assert "pages/post_list.html" in [
        t.name for t in response.templates
    ], "Template 'post_list.html' should be used."
