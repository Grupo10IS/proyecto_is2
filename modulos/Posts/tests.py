import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from modulos.Authorization.permissions import *
from modulos.Categories.models import Category
from modulos.Posts.models import Post, Revision


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
    ps_len = len(response.context["posts"])
    assert ps_len == 0, f"Expected 0 posts, got {ps_len}"

    # Test home view with existing posts
    Post.objects.create(
        title="Test Post 1", content="Content of test post 1", status=Post.PUBLISHED
    )
    Post.objects.create(
        title="Test Post 2", content="Content of test post 2", status=Post.DRAFT
    )
    Post.objects.create(
        title="Test Post 3", content="Content of test post 3", status=Post.PUBLISHED
    )

    response = client.get(url)
    assert response.status_code == 200
    ps_len = len(response.context["posts"])
    assert ps_len == 2, f"Expected 2 posts, got {ps_len}"


@pytest.mark.django_db
def test_view_post(client):
    """
    Test the post detail view with an existing post and a non-existent post.
    """
    post = Post.objects.create(
        title="Test Post",
        content="Content of test post",
        tags="tag1, tag2",
        status=Post.PUBLISHED,
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

    post = Post.objects.create(
        title="Test Post",
        content="Content of test post",
        tags="tag1, tag2",
        status=Post.DRAFT,
    )

    # Test post detail view on a draft post without permission
    url = reverse("post_detail", args=[post.id])
    response = client.get(url)
    assert response.status_code == 400


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


@pytest.mark.django_db
def test_review_post_view(client):
    """
    Test the review post view for post revision creation
    """
    # Create user and login
    user = get_user_model().objects.create_user(
        username="testuser", password="password"
    )
    client.login(username="testuser", password="password")
    user.user_permissions.add(Permission.objects.get(codename=POST_EDIT_PERMISSION))

    # Create a post with valid data and status not DRAFT
    category = Category.objects.create(name="test_category", description="descripcion")
    post = Post.objects.create(
        title="New Test Post",
        content="Content for new test post",
        category=category,
        status=Post.PUBLISHED,  # Important: Set status to something other than DRAFT
        version=1,
        author=user,
    )

    # Verify post exists
    assert Post.objects.filter(
        title="New Test Post"
    ).exists(), "Post should exist in the database after creation."

    # Now, simulate editing the post
    url = reverse("edit_post", args=[post.id])
    data = {
        "title": "Updated Test Post",
        "content": "Updated content for test post",
        "category": category.id,
    }
    client.post(url, data)

    # Verify that the post is updated
    post.refresh_from_db()
    assert post.title == "Updated Test Post", "Post title should be updated"

    # Verify that a revision was created
    assert Revision.objects.filter(post_id=post.id).exists(), "A revision should be created"
    revision = Revision.objects.get(post_id=post.id)
    assert (
        revision.version == post.version - 1
    ), "Revision version should be one less than the updated post version"
