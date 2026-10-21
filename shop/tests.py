from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal
from .models import Category, Product, Review


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Electrónica', slug='electronica')

    def test_category_creation(self):
        self.assertEqual(str(self.category), 'Electrónica')
        self.assertEqual(self.category.slug, 'electronica')

    def test_category_absolute_url(self):
        expected_url = reverse('shop:product_list_by_category', args=[self.category.slug])
        self.assertEqual(self.category.get_absolute_url(), expected_url)


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Ropa', slug='ropa')
        self.product = Product.objects.create(
            category=self.category,
            name='Camiseta Básica',
            slug='camiseta-basica',
            price=Decimal('19.99'),
            stock=50,
            available=True,
            description='Camiseta 100% algodón'
        )

    def test_product_creation(self):
        self.assertEqual(str(self.product), 'Camiseta Básica')
        self.assertEqual(self.product.price, Decimal('19.99'))
        self.assertEqual(self.product.stock, 50)
        self.assertTrue(self.product.available)

    def test_product_absolute_url(self):
        expected_url = reverse('shop:product_detail', args=[self.product.id, self.product.slug])
        self.assertEqual(self.product.get_absolute_url(), expected_url)


class ShopViewsTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Hogar', slug='hogar')
        self.product = Product.objects.create(
            category=self.category,
            name='Lámpara LED',
            slug='lampara-led',
            price=Decimal('25.50'),
            stock=15,
            available=True
        )

    def test_product_list_view(self):
        response = self.client.get(reverse('shop:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lámpara LED')

    def test_product_list_by_category_view(self):
        response = self.client.get(reverse('shop:product_list_by_category', args=[self.category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lámpara LED')

    def test_product_detail_view(self):
        response = self.client.get(reverse('shop:product_detail', args=[self.product.id, self.product.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Lámpara LED')

    def test_contact_view(self):
        response = self.client.get(reverse('shop:contact'))
        self.assertEqual(response.status_code, 200)


class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='password123')
        self.category = Category.objects.create(name='Libros', slug='libros')
        self.product = Product.objects.create(
            category=self.category,
            name='Libro Django',
            slug='libro-django',
            price=Decimal('30.00'),
            stock=5
        )
        self.review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment='Excelente libro para aprender Django'
        )

    def test_review_creation(self):
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Excelente libro para aprender Django')
        self.assertIn('tester', str(self.review))
