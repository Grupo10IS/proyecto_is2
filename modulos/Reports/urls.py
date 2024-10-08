from django.urls import path

from .views import *

urlpatterns = [
    path("", manage_reports, name="reports"),
    path("create/<int:id>", create_report, name="create_report"),
    path("detail/<int:id>", report_detail, name="report_detail"),
    path("review/<int:id>", review, name="review"),
]
