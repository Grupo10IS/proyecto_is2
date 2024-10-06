import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from modulos.Categories.models import Category
from modulos.Pagos.models import Payment

User = get_user_model()


@pytest.mark.django_db
def test_financial_view_access(client):
    # Crear un usuario financiero
    financial_user = User.objects.create_user(
        username="financial", password="financial123"
    )
    permission = Permission.objects.get(codename="view_purchased_categories")
    financial_user.user_permissions.add(permission)

    # Loguear al usuario financiero
    client.login(username="financial", password="financial123")

    # Probar que el usuario puede acceder a la vista
    url = reverse("financial_view")
    response = client.get(url)
    assert response.status_code == 200

    # Probar un usuario sin permisos
    regular_user = User.objects.create_user(username="regular", password="regular123")
    client.login(username="regular", password="regular123")
    response = client.get(url)
    assert (
        response.status_code == 403
    )  # Debería devolver un Forbidden (403) para usuarios sin permisos
