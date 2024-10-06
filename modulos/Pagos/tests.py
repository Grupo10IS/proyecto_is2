import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.contrib.auth import get_user_model
from modulos.Categories.models import Category
from modulos.Pagos.models import Payment

User = get_user_model()


@pytest.mark.django_db
def test_financial_view_access(client):
    # Crear un usuario financiero con un email único
    financial_user = User.objects.create_user(
        username="financial",
        email="financial@example.com",  # Asegúrate de que el email es único
        password="financialpass",
    )
    permission = Permission.objects.get(codename="view_purchased_categories")
    financial_user.user_permissions.add(permission)

    # Loguear al usuario financiero
    client.login(username="financial", password="financialpass")

    # Probar que el usuario puede acceder a la vista
    url = reverse("financial_view")
    response = client.get(url)
    assert response.status_code == 200

    # Probar un usuario regular sin permisos con un email único
    regular_user = User.objects.create_user(
        username="regular",
        email="regular@example.com",  # Asegúrate de que el email es único
        password="regularpass",
    )

    # Probar que el usuario sin permisos no puede acceder a la vista financiera
    client.login(username="regular", password="regularpass")
    response = client.get(url)
    assert response.status_code == 403  # Forbidden, el usuario no tiene permisos
