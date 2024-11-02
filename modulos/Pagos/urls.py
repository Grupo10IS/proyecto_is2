from django.urls import path
from .views import (
    financial_view,
    payment_success,
    payment_view,
    purchased_categories_view,
    user_payment_view,
    export_payments_excel,
    export_user_payments_excel,
)

urlpatterns = [
    path("pay/<int:category_id>/", payment_view, name="payment_view"),
    path("success/<int:category_id>/", payment_success, name="payment_success"),
    path(
        "mis-categorias-premium/",
        purchased_categories_view,
        name="purchased_categories",
    ),
    path("panel/", financial_view, name="financial_view"),
    path("mis-pagos/", user_payment_view, name="user_payment_view"),
    path("export/excel/", export_payments_excel, name="export_payments_excel"),
    path(
        "export_user_payments_excel/",
        export_user_payments_excel,
        name="export_user_payments_excel",
    ),
]
