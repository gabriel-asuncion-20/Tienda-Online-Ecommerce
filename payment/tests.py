from django.test import TestCase
from django.urls import reverse
from orders.models import Order


class PaymentViewsTest(TestCase):
    def setUp(self):
        self.order = Order.objects.create(
            first_name='Pedro',
            last_name='Picapiedra',
            email='pedro@example.com',
            phone='5551234',
            address='Rocadura 10',
            postal_code='00001',
            city='Piedras'
        )

    def test_payment_completed_view(self):
        response = self.client.get(reverse('payment:completed'))
        self.assertEqual(response.status_code, 200)

    def test_payment_canceled_view(self):
        response = self.client.get(reverse('payment:canceled'))
        self.assertEqual(response.status_code, 200)

    def test_payment_process_post_marks_paid(self):
        # Guardar order_id en la sesión
        session = self.client.session
        session['order_id'] = self.order.id
        session.save()

        response = self.client.post(reverse('payment:process'))
        self.assertRedirects(response, reverse('payment:completed'))

        self.order.refresh_from_db()
        self.assertTrue(self.order.paid)
