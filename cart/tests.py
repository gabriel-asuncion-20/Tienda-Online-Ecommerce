from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from decimal import Decimal
from shop.models import Category, Product
from .cart import Cart


class CartViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Gadgets', slug='gadgets')
        self.product = Product.objects.create(
            category=self.category,
            name='Auriculares Bluetooth',
            slug='auriculares-bluetooth',
            price=Decimal('50.00'),
            stock=20
        )

    def test_cart_detail_view(self):
        response = self.client.get(reverse('cart:cart_detail'))
        self.assertEqual(response.status_code, 200)

    def test_cart_add_product(self):
        response = self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 2, 'override': False}
        )
        self.assertRedirects(response, reverse('cart:cart_detail'))

        # Verificar que el producto está en la sesión
        session = self.client.session
        cart = session.get('cart')
        self.assertIsNotNone(cart)
        self.assertIn(str(self.product.id), cart)
        self.assertEqual(cart[str(self.product.id)]['quantity'], 2)

    def test_cart_remove_product(self):
        # Primero añadimos
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'override': False}
        )
        # Luego removemos
        response = self.client.post(reverse('cart:cart_remove', args=[self.product.id]))
        self.assertRedirects(response, reverse('cart:cart_detail'))

        session = self.client.session
        cart = session.get('cart')
        self.assertNotIn(str(self.product.id), cart)


class CartClassTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.category = Category.objects.create(name='Calzado', slug='calzado')
        self.product1 = Product.objects.create(
            category=self.category,
            name='Zapatillas Running',
            slug='zapatillas-running',
            price=Decimal('100.00'),
            stock=10
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name='Calcetines',
            slug='calcetines',
            price=Decimal('10.00'),
            stock=30
        )

    def _get_request_with_session(self):
        request = self.factory.get('/')
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()
        return request

    def test_cart_operations(self):
        request = self._get_request_with_session()
        cart = Cart(request)

        # Agregar productos
        cart.add(self.product1, quantity=1)
        cart.add(self.product2, quantity=3)

        self.assertEqual(len(cart), 4)
        self.assertEqual(cart.get_total_price(), 130.00)

        # Vaciar carrito
        cart.clear()
        self.assertEqual(len(cart), 0)
        self.assertEqual(cart.get_total_price(), 0)
