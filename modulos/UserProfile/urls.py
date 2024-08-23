from django.contrib.auth import views as auth_views
from django.urls import path

from modulos.UserProfile.views import CustomLoginView, SignUpView

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),  # Vista de login
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
]
