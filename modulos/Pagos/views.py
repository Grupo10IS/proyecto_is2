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
            amount=500,  # 500 centavos, equivale a 5 reales para Stripe
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
            # Aquí no se debe validar el estado del PaymentIntent.
            # El frontend se encarga de esto.
            # Redirigir a la página de éxito, después de confirmar el pago en el frontend.
            return redirect("payment_success", category_id=category.id)
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


# Vista para la página de éxito del pago
def payment_success(request, category_id):
    print(f">>> Redirigiendo a la página de éxito para la categoría ID: {category_id}")
    category = get_object_or_404(Category, id=category_id)
    user = request.user

    # Buscar el pago existente basado en el PaymentIntent ID
    payment = Payment.objects.filter(
        user=user, category=category, status="pending"
    ).first()

    if payment:
        try:
            # Verificar el estado del PaymentIntent
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_id)
            if intent.status == "succeeded":
                # Actualizar el estado a 'succeeded'
                payment.status = "succeeded"
                payment.save()
                print(
                    f"Pago actualizado exitosamente para la categoría {category.name}"
                )
            else:
                print(f"El PaymentIntent no ha sido exitoso. Estado: {intent.status}")
                return render(
                    request,
                    "payment_error.html",
                    {
                        "error": f"El pago no se completó correctamente. Estado: {intent.status}"
                    },
                )
        except Exception as e:
            print(f"Error al verificar el estado del PaymentIntent: {str(e)}")
            return render(request, "payment_error.html", {"error": str(e)})

    return render(request, "payment_success.html", {"category": category})
