"""Authentication tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import make_role


class AuthTests(APITestCase):
    def setUp(self):
        make_role('user')
        make_role('admin')
        self.register_url = reverse('authentication:register')
        self.login_url = reverse('authentication:login')

    def test_register_user(self):
        payload = {
            'firstName': 'John',
            'lastName': 'Doe',
            'userName': 'johndoe',
            'email': 'john@example.com',
            'password': 'StrongPass123!',
            'passwordConfirm': 'StrongPass123!',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'john@example.com')

    def test_register_password_mismatch(self):
        payload = {
            'firstName': 'John',
            'lastName': 'Doe',
            'userName': 'johndoe',
            'email': 'john@example.com',
            'password': 'StrongPass123!',
            'passwordConfirm': 'Different123!',
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_tokens(self):
        from apps.core.test_factories import make_user
        make_user(email='login@example.com', user_name='loginuser', password='TestPass123!')
        response = self.client.post(
            self.login_url,
            {'email': 'login@example.com', 'password': 'TestPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        response = self.client.post(
            self.login_url,
            {'email': 'nonexistent@example.com', 'password': 'WrongPass1!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
