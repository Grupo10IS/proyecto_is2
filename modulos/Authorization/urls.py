from django.urls import path

from .views import role_create, role_delete, role_information, role_list

urlpatterns = [
    path("", role_list, name="role_list"),
    path("create", role_create, name="role_create"),
    path("delete/<int:id>", role_delete, name="role_delete"),
    path("<int:id>", role_information, name="role_info"),
]
