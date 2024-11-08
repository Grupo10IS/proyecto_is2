from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Payment, Category

User = get_user_model()


class PaymentModelTests(TestCase):

    def setUp(self):
        # Crear un usuario de prueba
        self.user = User.objects.create_user(username='testuser', password='12345')

        # Crear una categoría de prueba
        self.category = Category.objects.create(name="TestCategory")

    def test_creacion_nuevo_pago(self):
        # Crea un nuevo objeto Payment
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=100.00,
            date_paid=timezone.now(),
            stripe_payment_id='test_id',
            status='completed',
            payment_method='credit_card',
            funding_type='credit',
            card_brand='visa',
            last4='1234'
        )

        # Comprueba que el pago fue creado correctamente
        self.assertEqual(nuevo_pago.user.username, 'testuser')
        self.assertEqual(nuevo_pago.category.name, 'TestCategory')
        self.assertEqual(nuevo_pago.amount, 100.00)
        self.assertEqual(nuevo_pago.stripe_payment_id, 'test_id')
        self.assertEqual(nuevo_pago.status, 'completed')
        self.assertEqual(nuevo_pago.payment_method, 'credit_card')
        self.assertEqual(nuevo_pago.funding_type, 'credit')
        self.assertEqual(nuevo_pago.card_brand, 'visa')
        self.assertEqual(nuevo_pago.last4, '1234')

    def test_valor_predeterminado(self):
        # Crear un nuevo objeto Payment con valores predeterminados
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=50.00
        )

        # Verificar valores predeterminados
        self.assertEqual(nuevo_pago.status, 'pending')
        self.assertEqual(nuevo_pago.payment_method, 'credit_card')

    def test_pago_con_metodo_debito(self):
        # Crear un nuevo objeto Payment con método de pago de débito
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=75.00,
            payment_method='debit_card',
            card_brand='mastercard',
            last4='5678'
        )

        # Verificar valores específicos
        self.assertEqual(nuevo_pago.payment_method, 'debit_card')
        self.assertEqual(nuevo_pago.card_brand, 'mastercard')
        self.assertEqual(nuevo_pago.last4, '5678')

    def test_str_method(self):
        # Crear un nuevo objeto Payment
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=30.00
        )
        # Verificar el método __str__
        self.assertEqual(str(nuevo_pago), f"Payment {self.user.username} for {self.category.name}")

    def test_actualizacion_pago(self):
        # Crear un nuevo objeto Payment
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=30.00
        )
        # Actualizar el pago
        nuevo_pago.amount = 40.00
        nuevo_pago.save()

        # Verificar el monto actualizado
        self.assertEqual(nuevo_pago.amount, 40.00)

    def test_eliminacion_pago(self):
        # Crear un nuevo objeto Payment
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=30.00
        )
        # Eliminar el pago
        nuevo_pago_id = nuevo_pago.id
        nuevo_pago.delete()

        # Verificar que el pago fue eliminado
        with self.assertRaises(Payment.DoesNotExist):
            Payment.objects.get(id=nuevo_pago_id)

    def test_fecha_pago_futura(self):
        futuro = timezone.now() + timezone.timedelta(days=1)
        nuevo_pago = Payment.objects.create(
            user=self.user,
            category=self.category,
            amount=50.00,
            date_paid=futuro
        )
        self.assertGreaterEqual(nuevo_pago.date_paid, timezone.now())
