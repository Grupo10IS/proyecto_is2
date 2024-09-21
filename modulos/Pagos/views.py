from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from modulos.Pagos.models import Payment
from modulos.Categories.models import Category
from modulos.Pagos.forms import PaymentForm, UserProfileForm
from django.shortcuts import get_object_or_404
import stripe

# Configura tu clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@login_required
def payment_view(request, category_id):
    print(">>> Entrando a la vista 'payment_view'")
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
        print(f"PaymentIntent creado correctamente. Client Secret: {client_secret}")

        # Crear un nuevo registro de pago con estado 'pending'
        Payment.objects.create(
            user=user,
            category=category,
            amount=5.00,  # Ajustar el monto según sea necesario
            stripe_payment_id=intent.id,  # Almacenar el PaymentIntent ID
            status="pending",  # Inicialmente en 'pending'
        )

    except Exception as e:
        print(f"Error creando PaymentIntent: {str(e)}")
        return render(request, "payment_error.html", {"error": str(e)})

    if request.method == "POST":
        print(">>> POST request recibido, procesando formularios.")
        profile_form = UserProfileForm(request.POST, instance=user)
        payment_form = PaymentForm(request.POST)

        if profile_form.is_valid() and payment_form.is_valid():
            print(">>> Formulario de perfil es válido. Guardando datos.")
            # Guardar el perfil del usuario actualizado
            profile_form.save()

            # Verificar el estado del PaymentIntent antes de redirigir
            intent = stripe.PaymentIntent.retrieve(intent.id)
            if intent.status == "succeeded":
                # Redirigir a la página de éxito
                return redirect("payment_success", category_id=category.id)
            else:
                print(
                    f"Error: El estado del PaymentIntent no es 'succeeded', es: {intent.status}"
                )
                return render(
                    request,
                    "payment_form.html",
                    {
                        "profile_form": profile_form,
                        "payment_form": payment_form,
                        "category": category,
                        "client_secret": client_secret,
                        "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                        "payment_error": f"El pago no se completó correctamente. Estado: {intent.status}",
                    },
                )
        else:
            # Si hay un error en el formulario, mostrar los errores
            print(f"Errores en el formulario de perfil: {profile_form.errors}")
            print(f"Errores en el formulario de pago: {payment_form.errors}")
            return render(
                request,
                "payment_form.html",
                {
                    "profile_form": profile_form,
                    "payment_form": payment_form,
                    "category": category,
                    "client_secret": client_secret,
                    "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,
                },
            )

    else:  # GET request
        print(">>> GET request recibido. Mostrando el formulario inicial.")
        profile_form = UserProfileForm(instance=user)
        payment_form = PaymentForm(initial={"amount": 5.00})

    print(">>> Renderizando el formulario de pago con el client_secret.")
    return render(
        request,
        "payment_form.html",
        {
            "profile_form": profile_form,
            "payment_form": payment_form,
            "category": category,
            "client_secret": client_secret,  # Pasar siempre el client_secret
            "STRIPE_PUBLIC_KEY": settings.STRIPE_PUBLIC_KEY,  # Pasar la clave pública de Stripe
        },
    )


@login_required
def payment_success(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    try:
        # Recuperar el PaymentIntent desde la base de datos
        payment = Payment.objects.filter(user=user, category=category).latest(
            "date_paid"
        )
        intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)

        if intent.status == "succeeded":
            # Actualizar el estado del pago en la base de datos
            payment.status = "completed"
            payment.save()

            # Redirigir a la página de éxito
            return render(request, "payment_success.html", {"category": category})
        else:
            print(f"El PaymentIntent no ha sido exitoso. Estado: {intent.status}")
            return render(
                request,
                "payment_error.html",
                {
                    "error": f"El pago no se completó correctamente. Estado: {intent.status}"
                },
            )

    except Payment.DoesNotExist:
        print("Error: No se encontró el pago en la base de datos.")
        return render(
            request,
            "payment_error.html",
            {"error": "No se encontró el pago en la base de datos."},
        )
