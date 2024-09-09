import pytest
from django.urls import reverse

from modulos.UserProfile.management.commands.new_admin import (_credentials,
                                                               create_admin)
from modulos.UserProfile.models import UserProfile


@pytest.mark.django_db
def test_register_view(client):
    url = reverse("signup")
    response = client.get(url)
    assert response.status_code == 200

    data = {
        "username": "testuser",
        "password1": "testpassword",
        "password2": "testpassword",
    }
    response = client.post(url, data)

    # assert response.status_code == 302  # Redirección tras el registro


@pytest.mark.django_db
def test_login_view(client):
    # Crear un usuario de prueba
    user = UserProfile.objects.create(
        username="testuser", password="testpassword"
    ).save()

    url = reverse("login")
    response = client.get(url)
    assert response.status_code == 200

    data = {
        "username": "testuser",
        "password": "testpassword",
    }
    response = client.post(url, data)

    # assert response.status_code == 302  # Redirección tras el login
    # assert response.url == '/'  # Redirige a la página de inicio


@pytest.mark.django_db
def test_user_list_view(client, django_user_model):
    # Crear un usuario de prueba sin permisos

    admin_user = django_user_model.objects.create_user(
        username="admin", password="adminpassword", email="admin@example.com"
    )
    client.login(username="admin", password="adminpassword")

    url = reverse("user_list")
    response = client.get(url)
    assert response.status_code == 403

    # Crear un usuario de prueba con permisos

    create_admin(
        _credentials(
            username="true_admin",
            paswd="password",
            pas_conf="password",
            email="adimns@gmail.com",
        )
    )

    client.login(username="true_admin", password="password")

    url = reverse("user_list")
    response = client.get(url)
    assert response.status_code == 200
