from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class AccountsViewTest(TestCase):
    def setUp(self):
        self.username = 'juanperez'
        self.email = 'juan@example.com'
        self.password = 'SuperPassword123!'
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )

    def test_register_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_post_success(self):
        data = {
            'username': 'nuevo_usuario',
            'email': 'nuevo@example.com',
            'password1': 'MiClaveSecreta999!',
            'password2': 'MiClaveSecreta999!',
        }
        response = self.client.post(reverse('register'), data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())

    def test_login_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_success(self):
        response = self.client.post(reverse('login'), {
            'username': self.username,
            'password': self.password,
        })
        # Login redirige según LOGIN_REDIRECT_URL ('/')
        self.assertRedirects(response, '/')

    def test_logout(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('logout'))
        # Logout redirige según LOGOUT_REDIRECT_URL ('/')
        self.assertEqual(response.status_code, 302)
