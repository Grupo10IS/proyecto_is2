from django.contrib.auth import views as auth_views
from django.urls import path

from modulos.UserProfile.views import CustomLoginView, SignUpView

from .forms import CustomPasswordResetForm
from .views import (manage_user_groups, profile_view, user_delete, user_edit,
                    user_list)

urlpatterns = [
    path("", user_list, name="user_list"),
    path("login/", CustomLoginView.as_view(), name="login"),  # Vista de login
    path("signup/", SignUpView.as_view(), name="signup"),  # Vista de registro
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="registration/password_reset.html",
            form_class=CustomPasswordResetForm,
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        ),
        name="password_reset",
    ),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="registration/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="registration/password_reset_confirmation.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="registration/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path("edit/<int:user_id>/", user_edit, name="user_edit"),
    path("delete/<int:user_id>/", user_delete, name="user_delete"),
    path("groups/<int:user_id>/", manage_user_groups, name="manage_user_groups"),
]
