from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import generic

from .forms import CustomUserCreationForm


class SignUpView(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class CustomLoginView(LoginView):
    redirect_authenticated_user = True  # Redirect if already logged in

    def get_redirect_url(self):
        # Default redirection
        redirect_to = self.request.POST.get("next", "")

        # FIX: cambiar el url de admin a home
        return redirect_to or reverse_lazy("admin:index")
