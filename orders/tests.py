from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from shop.models import Category, Product
from .models import Order, OrderItem


class OrderModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Oficina', slug='oficina')
        self.product1 = Product.objects.create(
            category=self.category,
            name='Silla Ergonómica',
            slug='silla-ergonomica',
            price=Decimal('150.00'),
            stock=10
        )
        self.product2 = Product.objects.create(
            category=self.category,
            name='Mouse Pad',
            slug='mouse-pad',
            price=Decimal('15.00'),
            stock=50
        )
        self.order = Order.objects.create(
            first_name='Carlos',
            last_name='Gomez',
            email='carlos@example.com',
            phone='123456789',
            address='Calle Falsa 123',
            postal_code='12345',
            city='Bogota'
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product1,
            price=self.product1.price,
            quantity=1
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            price=self.product2.price,
            quantity=2
        )

    def test_order_creation_and_cost(self):
        self.assertEqual(str(self.order), f'Order {self.order.id}')
        # 150*1 + 15*2 = 180
        self.assertEqual(self.order.get_total_cost(), Decimal('180.00'))
        self.assertFalse(self.order.paid)


class OrderViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cliente', password='password123')
        self.category = Category.objects.create(name='General', slug='general')
        self.product = Product.objects.create(
            category=self.category,
            name='Teclado Mecanico',
            slug='teclado-mecanico',
            price=Decimal('75.00'),
            stock=15
        )

    def test_order_create_view_get(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 200)

    def test_order_create_view_post_success(self):
        # 1. Agregar producto al carrito
        self.client.post(
            reverse('cart:cart_add', args=[self.product.id]),
            {'quantity': 1, 'override': False}
        )

        # 2. Enviar formulario de orden
        order_data = {
            'first_name': 'Ana',
            'last_name': 'Perez',
            'email': 'ana@example.com',
            'phone': '987654321',
            'address': 'Av Principal 456',
            'postal_code': '10001',
            'city=': 'Lima',
            'city': 'Lima'
        }
        response = self.client.post(reverse('orders:order_create'), order_data)
        self.assertRedirects(response, reverse('payment:process'))
        self.assertTrue(Order.objects.filter(email='ana@example.com').exists())

    def test_order_history_requires_login(self):
        # Usuario anónimo debe ser redirigido a login
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 302)

    def test_order_history_authenticated(self):
        self.client.login(username='cliente', password='password123')
        # Crear orden asociada al usuario
        Order.objects.create(
            user=self.user,
            first_name='Cliente',
            last_name='User',
            email='cliente@example.com',
            phone='12345678',
            address='Calle 1',
            postal_code='10101',
            city='Quito'
        )
        response = self.client.get(reverse('orders:order_history'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'HISTORIAL DE PEDIDOS')
