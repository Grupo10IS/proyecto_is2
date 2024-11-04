from django.urls import path

from .views import (export_payments_excel, export_user_payments_excel,
                    financial_view, payment_success, payment_view,
                    purchased_categories_view, user_payment_view)

urlpatterns = [
    # vistas
    path("", user_payment_view, name="user_payment_view"),
    path(
        "purchased/",
        purchased_categories_view,
        name="purchased_categories",
    ),
    path("admin/", financial_view, name="financial_view"),
    # crud
    path("pay/<int:category_id>/", payment_view, name="payment_view"),
    path("success/<int:category_id>/", payment_success, name="payment_success"),
    # exportacion de reportes
    path("admin/export/", export_payments_excel, name="export_payments_excel"),
    path(
        "export",
        export_user_payments_excel,
        name="export_user_payments_excel",
    ),
]
