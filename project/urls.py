"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path

from modulos.Authorization import urls as roles_urls
from modulos.Posts.views import HomeView, AdminHomeView
from modulos.UserProfile import urls as user_urls

urlpatterns = [
    path("admin-home/", AdminHomeView.as_view(), name="admin_home"),
    path("", HomeView.as_view(), name="home"),
    path("users/", include(user_urls)),
    path("roles/", include(roles_urls)),
]
