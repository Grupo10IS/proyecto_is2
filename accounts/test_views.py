import pytest
from django.urls import reverse
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_register_view(client):
    url = reverse('register')
    response = client.get(url)
    assert response.status_code == 200

    data = {
        'username': 'testuser',
        'password1': 'testpassword',
        'password2': 'testpassword',
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirección tras el registro

@pytest.mark.django_db
def test_login_view(client):
    # Crear un usuario de prueba
    user = User.objects.create_user(username='testuser', password='testpassword')

    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200

    data = {
        'username': 'testuser',
        'password': 'testpassword',
    }
    response = client.post(url, data)
    assert response.status_code == 302  # Redirección tras el login
    assert response.url == '/'  # Redirige a la página de inicio
