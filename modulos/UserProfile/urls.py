from django.contrib.auth import views as auth_views
from django.urls import path
from .views import user_list, user_edit, user_delete, manage_user_groups

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
    path("users/", user_list, name="user_list"),
    path("users/edit/<int:user_id>/", user_edit, name="user_edit"),
    path("users/delete/<int:user_id>/", user_delete, name="user_delete"),
    path("users/groups/<int:user_id>/", manage_user_groups, name="manage_user_groups"),
    # Otras rutas que ya tenías definidas
]
