import json

import openpyxl
import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from modulos.Authorization.permissions import VIEW_PURCHASED_CATEGORIES
from modulos.Categories.models import Category
from modulos.Pagos.forms import PaymentFilterForm, PaymentForm, UserProfileForm
from modulos.Pagos.models import Payment
from modulos.utils import new_ctx

# Configura tu clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_view(request, category_id):
    category = Category.objects.get(id=category_id)
    user = request.user

    try:
        # Crear el PaymentIntent y obtener el client_secret
        intent = stripe.PaymentIntent.create(
            amount=500,  # 500 centavos, equivale a 5 reales para Stripe equivale a 1 dólar americano
            currency="BRL",  # Cambiar a BRL
            payment_method_types=["card"],
            metadata={"category_id": category.id, "user_id": user.id},
        )
        client_secret = intent.client_secret

        # Crear un nuevo registro de pago con estado 'pending'
        Payment.objects.create(
            user=user,
            category=category,
            amount=5.00,  # Ajustar el monto según sea necesario
            stripe_payment_id=intent.id,  # Almacenar el PaymentIntent ID
            status="pending",  # Inicialmente en 'pending'
        )

    except Exception as e:
        return render(
            request, "payment_error.html", new_ctx(request, {"error": str(e)})
        )

    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, instance=user)
        payment_form = PaymentForm(request.POST)

        if profile_form.is_valid() and payment_form.is_valid():
            # Guardar el perfil del usuario actualizado
            profile_form.save()

            # Verificar el estado del PaymentIntent antes de redirigir
            intent = stripe.PaymentIntent.retrieve(intent.id)
            if not intent.status == "succeeded":
                return render(
                    request,
                    "payment_form.html",
                    new_ctx(
                        request,
                        {
                            "profile_form": profile_form,
                            "payment_form": payment_form,
                            "category": category,
                            "client_secret": client_secret,
                            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                            "payment_error": f"El pago no se completó correctamente. Estado: {intent.status}",
                        },
                    ),
                )

            # Redirigir a la página de éxito
            return redirect("payment_success", category_id=category.id)

        # Si hay un error en el formulario, mostrar los errores
        return render(
            request,
            "payment_form.html",
            new_ctx(
                request,
                {
                    "profile_form": profile_form,
                    "payment_form": payment_form,
                    "category": category,
                    "client_secret": client_secret,
                    "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                },
            ),
        )

    profile_form = UserProfileForm(instance=user)
    payment_form = PaymentForm(initial={"amount": 5.00})

    return render(
        request,
        "payment_form.html",
        new_ctx(
            request,
            {
                "profile_form": profile_form,
                "payment_form": payment_form,
                "category": category,
                "client_secret": client_secret,  # Pasar siempre el client_secret
                "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,  # Pasar la clave pública de Stripe
            },
        ),
    )


@login_required
def payment_success(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    try:
        # Recuperar el PaymentIntent y su registro en la base de datos
        payment = Payment.objects.filter(user=user, category=category).latest(
            "date_paid"
        )
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)

        # Verificar que el pago se completó correctamente
        if intent.status != "succeeded":
            return render(
                request,
                "payment_error.html",
                new_ctx(
                    request,
                    {
                        "error": f"El pago no se completó correctamente. Estado: {intent.status}"
                    },
                ),
            )

        # Obtener detalles de la tarjeta del método de pago
        payment_method = stripe.PaymentMethod.retrieve(intent.payment_method)
        card = payment_method.card

        # Actualizar el estado y detalles del pago en la base de datos
        payment.status = "completed"
        payment.funding_type = (
            card.funding
        )  # Almacenar "credit", "debit", "prepaid", o "unknown"
        payment.card_brand = (
            card.brand
        )  # Almacenar la marca de tarjeta, como Visa, Mastercard
        payment.last4 = card.last4  # Almacenar los últimos 4 dígitos
        payment.save()

        # Pasar `payment` al contexto
        return render(
            request,
            "payment_success.html",
            new_ctx(request, {"category": category, "payment": payment}),
        )

    except Payment.DoesNotExist:
        return render(
            request,
            "payment_error.html",
            new_ctx(request, {"error": "No se encontró el pago en la base de datos."}),
        )


@login_required
def purchased_categories_view(request):
    """
    Vista para mostrar todas las categorías premium compradas por el usuario.
    """
    # Filtrar las categorías compradas por el usuario con pagos completados
    purchased_categories = Payment.objects.filter(
        user=request.user, status="completed"
    ).select_related("category")

    context = new_ctx(
        request,
        {
            "purchased_categories": purchased_categories,
        },
    )

    return render(request, "purchased_categories.html", context)


@login_required
@permission_required([VIEW_PURCHASED_CATEGORIES])
def financial_view(request):
    form = PaymentFilterForm(request.GET or None)

    # Construimos la query inicial (mostrar todos los pagos completados)
    payments_queryset = Payment.objects.filter(status="completed").order_by(
        "-date_paid"
    )

    # Aplicamos filtros si el formulario es válido
    if form.is_valid():
        category = form.cleaned_data.get("category")
        user = form.cleaned_data.get("user")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")
        card_brand = form.cleaned_data.get("card_brand")
        funding_type = form.cleaned_data.get("funding_type")

        if category:
            payments_queryset = payments_queryset.filter(category=category)
        if user:
            payments_queryset = payments_queryset.filter(user__username__icontains=user)
        if date_from:
            payments_queryset = payments_queryset.filter(date_paid__gte=date_from)
        if date_to:
            payments_queryset = payments_queryset.filter(date_paid__lte=date_to)
        if card_brand:
            payments_queryset = payments_queryset.filter(card_brand__iexact=card_brand)
        if funding_type:
            payments_queryset = payments_queryset.filter(
                funding_type__iexact=funding_type
            )

    # Filtrar duplicados: Mantener solo el pago más reciente por (usuario, categoría)
    unique_payments = {}
    for payment in payments_queryset:
        key = (payment.user, payment.category)
        if key not in unique_payments:
            unique_payments[key] = payment
    payments = list(unique_payments.values())

    # Calcular el total de pagos recibidos sin duplicados
    total_amount = float(sum(payment.amount for payment in payments))

    # Preparar datos para el gráfico de torta (número de compras por categoría sin duplicados)
    category_totals = {}
    for payment in payments:
        category_name = payment.category.name
        category_totals[category_name] = category_totals.get(category_name, 0) + 1

    category_labels = list(category_totals.keys())
    category_data = [float(value) for value in category_totals.values()]

    # Preparar datos para el gráfico de barras (monto total por fecha sin duplicados)
    date_totals = {}
    for payment in payments:
        date_str = timezone.localtime(payment.date_paid).strftime("%Y-%m-%d")
        date_totals[date_str] = date_totals.get(date_str, 0) + float(payment.amount)

    date_labels = list(date_totals.keys())
    date_data = list(date_totals.values())

    # Preparar datos para el gráfico de líneas (comparativa de categorías por fecha sin duplicados)
    category_by_date = {}
    for payment in payments:
        category_name = payment.category.name
        date_str = timezone.localtime(payment.date_paid).strftime("%Y-%m-%d")
        if category_name not in category_by_date:
            category_by_date[category_name] = {"labels": [], "data": []}
        if date_str not in category_by_date[category_name]["labels"]:
            category_by_date[category_name]["labels"].append(date_str)
            category_by_date[category_name]["data"].append(float(payment.amount))
        else:
            # Sumar el monto a la fecha ya existente
            index = category_by_date[category_name]["labels"].index(date_str)
            category_by_date[category_name]["data"][index] += float(payment.amount)

    # Ordenar las fechas dentro de cada categoría para una línea de tiempo adecuada
    for category in category_by_date.values():
        sorted_data = sorted(zip(category["labels"], category["data"]))
        category["labels"], category["data"] = zip(*sorted_data)

    # Pasar los datos al contexto
    context = new_ctx(
        request,
        {
            "form": form,
            "payments": payments,
            "total_amount": total_amount,
            "category_labels": json.dumps(category_labels),
            "category_data": json.dumps(category_data),
            "date_labels": json.dumps(date_labels),
            "date_data": json.dumps(date_data),
            "category_by_date": json.dumps(category_by_date),
        },
    )

    return render(request, "financial_view.html", context)


@login_required
def user_payment_view(request):
    """
    Vista para que el usuario autenticado vea sus propios pagos.
    """
    form = PaymentFilterForm(request.GET or None)

    # Filtramos los pagos solo para el usuario actual
    payments = Payment.objects.filter(user=request.user, status="completed").order_by(
        "-date_paid"
    )

    # Aplicamos los filtros si el formulario es válido
    if form.is_valid():
        category = form.cleaned_data.get("category")
        card_brand = form.cleaned_data.get("card_brand")
        funding_type = form.cleaned_data.get("funding_type")
        date_from = form.cleaned_data.get("date_from")
        date_to = form.cleaned_data.get("date_to")

        if category:
            payments = payments.filter(category=category)
        if card_brand:
            payments = payments.filter(card_brand=card_brand)
        if funding_type:
            payments = payments.filter(funding_type=funding_type)
        if date_from:
            payments = payments.filter(date_paid__gte=date_from)
        if date_to:
            payments = payments.filter(date_paid__lte=date_to)

    # Filtrar duplicados: Mantener solo el pago más reciente por (usuario, categoría)
    unique_payments = {}
    for payment in payments:
        key = (payment.user, payment.category)
        if key not in unique_payments:
            unique_payments[key] = payment
    payments = list(unique_payments.values())

    # Calcular el total de los pagos
    total_amount = sum(payment.amount for payment in payments)

    context = new_ctx(
        request,
        {
            "form": form,
            "payments": payments,
            "total_amount": total_amount,  # Pasamos el total al contexto
        },
    )

    return render(request, "user_financial_view.html", context)


@login_required
def export_payments_excel(request):
    # Obtener los datos de pagos filtrados según los parámetros de la solicitud GET
    payments = Payment.objects.filter(status="completed").order_by("-date_paid")

    # Aplicar filtros basados en los parámetros de la solicitud GET
    category = request.GET.get("category")
    user = request.GET.get("user")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    card_brand = request.GET.get("card_brand")
    funding_type = request.GET.get("funding_type")

    if category:
        payments = payments.filter(category__id=category)
    if user:
        payments = payments.filter(user__username__icontains=user)
    if date_from:
        payments = payments.filter(date_paid__gte=date_from)
    if date_to:
        payments = payments.filter(date_paid__lte=date_to)
    if card_brand:
        payments = payments.filter(card_brand__iexact=card_brand)
    if funding_type:
        payments = payments.filter(funding_type__iexact=funding_type)

    # Filtrar duplicados: Mantener solo el pago más reciente por (usuario, categoría)
    unique_payments = {}
    for payment in payments:
        key = (payment.user, payment.category)
        if key not in unique_payments:
            unique_payments[key] = payment
    payments = list(unique_payments.values())

    # Crear el archivo Excel en memoria
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Pagos de Categorías Premium"

    # Agregar encabezados
    headers = [
        "Usuario",
        "Categoría",
        "Fecha de Pago",
        "Monto",
        "Marca de Tarjeta",
        "Tipo de Tarjeta",
        "Últimos 4 Dígitos",
    ]
    worksheet.append(headers)

    # Rellenar datos en el Excel
    for payment in payments:
        local_date_paid = timezone.localtime(payment.date_paid).strftime(
            "%d/%m/%Y %H:%M"
        )
        worksheet.append(
            [
                payment.user.username,
                payment.category.name,
                local_date_paid,  # Fecha en la zona horaria local
                f"R${payment.amount}",
                payment.card_brand or "N/A",
                (
                    "Crédito"
                    if payment.funding_type == "credit"
                    else (
                        "Débito"
                        if payment.funding_type == "debit"
                        else (
                            "Prepagada"
                            if payment.funding_type == "prepaid"
                            else "Desconocido"
                        )
                    )
                ),
                payment.last4 or "N/A",
            ]
        )

    # Preparar la respuesta HTTP para descargar el archivo
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="pagos_categorias_premium.xlsx"'
    )

    # Guardar el archivo en la respuesta HTTP
    workbook.save(response)
    return response


@login_required
def export_user_payments_excel(request):
    # Obtener los pagos completados solo del usuario autenticado
    payments = Payment.objects.filter(user=request.user, status="completed").order_by(
        "-date_paid"
    )

    # Aplicar filtros basados en los parámetros de la solicitud GET
    category = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    card_brand = request.GET.get("card_brand")
    funding_type = request.GET.get("funding_type")

    if category:
        payments = payments.filter(category__id=category)
    if date_from:
        payments = payments.filter(date_paid__gte=date_from)
    if date_to:
        payments = payments.filter(date_paid__lte=date_to)
    if card_brand:
        payments = payments.filter(card_brand__iexact=card_brand)
    if funding_type:
        payments = payments.filter(funding_type__iexact=funding_type)

    # Filtrar duplicados: Mantener solo el pago más reciente por categoría
    unique_payments = {}
    for payment in payments:
        key = payment.category
        if key not in unique_payments:
            unique_payments[key] = payment
    payments = list(unique_payments.values())

    # Crear el archivo Excel en memoria
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Mis Pagos de Categorías Premium"

    # Agregar encabezados
    headers = [
        "Categoría",
        "Fecha de Pago",
        "Monto",
        "Marca de Tarjeta",
        "Tipo de Tarjeta",
        "Últimos 4 Dígitos",
    ]
    worksheet.append(headers)

    # Rellenar datos en el Excel
    for payment in payments:
        local_date_paid = timezone.localtime(payment.date_paid).strftime(
            "%d/%m/%Y %H:%M"
        )
        worksheet.append(
            [
                payment.category.name,
                local_date_paid,  # Fecha en la zona horaria local
                f"R${payment.amount}",
                payment.card_brand or "N/A",
                (
                    "Crédito"
                    if payment.funding_type == "credit"
                    else (
                        "Débito"
                        if payment.funding_type == "debit"
                        else (
                            "Prepagada"
                            if payment.funding_type == "prepaid"
                            else "Desconocido"
                        )
                    )
                ),
                payment.last4 or "N/A",
            ]
        )

    # Preparar la respuesta HTTP para descargar el archivo
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = (
        'attachment; filename="mis_pagos_categorias_premium.xlsx"'
    )

    # Guardar el archivo en la respuesta HTTP
    workbook.save(response)
    return response
