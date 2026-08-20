"""Users tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import make_user


class MeTests(APITestCase):
    def setUp(self):
        self.user = make_user(email='me@example.com', user_name='meuser', password='TestPass123!')
        self.client.force_authenticate(user=self.user)
        self.me_url = reverse('users:user-me')

    def test_get_me(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'me@example.com')

    def test_patch_me(self):
        response = self.client.patch(self.me_url, {'firstName': 'Updated'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstName'], 'Updated')

    def test_change_password(self):
        url = reverse('users:user-change-password')
        response = self.client.post(
            url,
            {'currentPassword': 'TestPass123!', 'newPassword': 'NewStrongPass123!'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class AdminUserListTests(APITestCase):
    def setUp(self):
        self.admin = make_user(email='admin@example.com', user_name='adminuser', role_name='admin')
        self.user = make_user(email='regular@example.com', user_name='regularuser', role_name='user')

    def test_admin_can_list_users(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_list_users(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
