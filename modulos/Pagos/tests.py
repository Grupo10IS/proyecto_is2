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
        email="financial@example.com",
        password="financialpass",  # Asegúrate de establecer una contraseña
    )
    permission = Permission.objects.get(codename="view_purchased_categories")
    financial_user.user_permissions.add(permission)

    # Loguear al usuario financiero
    login_successful = client.login(username="financial", password="financialpass")
    assert login_successful, "El login del usuario financiero falló"

    # Probar que el usuario puede acceder a la vista financiera
    url = reverse("financial_view")
    response = client.get(url)
    assert response.status_code == 200  # El usuario financiero tiene acceso

    # Crear un usuario regular sin permisos con un email único
    regular_user = User.objects.create_user(
        username="regular",
        email="regular@example.com",
        password="regularpass",  # Asegúrate de establecer una contraseña
    )

    # Loguear al usuario regular sin permisos
    login_successful = client.login(username="regular", password="regularpass")
    assert login_successful, "El login del usuario regular falló"

    # Probar que el usuario sin permisos no puede acceder a la vista financiera
    response = client.get(url)
    assert response.status_code == 403  # Forbidden, el usuario no tiene permisos
