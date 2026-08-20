"""Splits tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import (
    make_split,
    make_split_day,
    make_user,
)


class SplitTests(APITestCase):
    def setUp(self):
        self.user = make_user(email='split@example.com', user_name='splituser')
        self.split = make_split()
        self.day = make_split_day(self.split, day_number=1, day_name='Push')

    def test_user_adopts_split(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('splits:my-split-list')
        response = self.client.post(
            url,
            {'idSplit': self.split.id, 'startDate': '2026-01-01', 'isActive': True},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['isActive'])

    def test_adopting_new_split_deactivates_old(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('splits:my-split-list')
        self.client.post(
            url,
            {'idSplit': self.split.id, 'startDate': '2026-01-01', 'isActive': True},
            format='json',
        )
        other = make_split(name='Upper/Lower')
        self.client.post(
            url,
            {'idSplit': other.id, 'startDate': '2026-02-01', 'isActive': True},
            format='json',
        )
        active_url = reverse('splits:my-split-active')
        response = self.client.get(active_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['idSplit'], other.id)
