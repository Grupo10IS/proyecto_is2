import pytest
from django.urls import reverse
from modulos.Categories.models import Category
from django.contrib.auth import get_user_model

from modulos.Authorization import permissions
from modulos.UserProfile.management.commands.new_admin import _credentials, create_admin


@pytest.mark.django_db
def test_category_create_view(client):
    # Crear un usuario administrador para las pruebas
    create_admin(
        _credentials(
            username="true_admin",
            paswd="password",
            pas_conf="password",
            email="admin@example.com",
        )
    )

    client.login(username="true_admin", password="password")

    url = reverse("category_create")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_category_edit_view(client):
    # Crear un usuario administrador para las pruebas
    create_admin(
        _credentials(
            username="true_admin",
            paswd="password",
            pas_conf="password",
            email="admin@example.com",
        )
    )

    client.login(username="true_admin", password="password")

    category = Category.objects.create(
        name="Test Category",
        description="A category for testing",
        status="ACTIVO",
        tipo="GRATIS",
    )

    url = reverse("category_edit", args=[category.pk])
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_category_delete_view(client):
    # Crear un usuario administrador para las pruebas
    create_admin(
        _credentials(
            username="true_admin",
            paswd="password",
            pas_conf="password",
            email="admin@example.com",
        )
    )

    client.login(username="true_admin", password="password")

    category = Category.objects.create(
        name="Test Category",
        description="A category for testing",
        status="ACTIVO",
        tipo="GRATIS",
    )

    url = reverse("category_delete", args=[category.pk])
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_category_create_view_non_admin(client):
    # Crear un usuario sin permisos especiales
    user = get_user_model().objects.create_user(
        username="normaluser", password="userpassword"
    )
    client.login(username="normaluser", password="userpassword")

    url = reverse("category_create")
    response = client.get(url)
    assert response.status_code == 403  # Acceso denegado


@pytest.mark.django_db
def test_category_edit_view_non_admin(client):
    # Crear un usuario sin permisos especiales
    user = get_user_model().objects.create_user(
        username="normaluser", password="userpassword"
    )
    client.login(username="normaluser", password="userpassword")

    category = Category.objects.create(
        name="Test Category",
        description="A category for testing",
        status="ACTIVO",
        tipo="GRATIS",
    )

    url = reverse("category_edit", args=[category.pk])
    response = client.get(url)
    assert response.status_code == 403  # Acceso denegado


@pytest.mark.django_db
def test_category_delete_view_non_admin(client):
    # Crear un usuario sin permisos especiales
    user = get_user_model().objects.create_user(
        username="normaluser", password="userpassword"
    )
    client.login(username="normaluser", password="userpassword")

    category = Category.objects.create(
        name="Test Category",
        description="A category for testing",
        status="ACTIVO",
        tipo="GRATIS",
    )

    url = reverse("category_delete", args=[category.pk])
    response = client.post(url)
    assert response.status_code == 403  # Acceso denegado
