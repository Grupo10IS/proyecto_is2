from django.urls import path
from django.contrib.auth import (
    views as auth_views,
)  # Asegúrate de tener esta importación
from accounts.views import SignUpView

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(), name="login"),  # Vista de login
    path("signup/", SignUpView.as_view(), name="signup"),  # Vista de registro
    path(
        "password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # Otras rutas que necesites
]
