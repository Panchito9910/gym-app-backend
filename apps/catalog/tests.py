"""Catalog tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import make_muscle, make_user


class MuscleTests(APITestCase):
    def setUp(self):
        self.trainer = make_user(email='trainer@example.com', user_name='traineruser', role_name='trainer')
        self.user = make_user(email='user@example.com', user_name='normaluser', role_name='user')
        self.muscle = make_muscle()
        self.url = reverse('catalog:muscle-list')

    def test_user_can_list_muscles(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_trainer_can_create_muscle(self):
        self.client.force_authenticate(user=self.trainer)
        response = self.client.post(self.url, {'name': 'Biceps braquial'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_create_muscle(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, {'name': 'Biceps braquial'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
