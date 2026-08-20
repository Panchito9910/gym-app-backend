"""Routines tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import (
    make_exercise,
    make_muscle,
    make_split,
    make_split_day,
    make_user,
)


class RoutineTests(APITestCase):
    def setUp(self):
        self.user = make_user(email='routine@example.com', user_name='routineuser')
        self.split = make_split()
        self.day = make_split_day(self.split)
        muscle = make_muscle()
        self.exercise = make_exercise(muscle=muscle)

        self.client.force_authenticate(user=self.user)
        split_url = reverse('splits:my-split-list')
        self.user_split = self.client.post(
            split_url,
            {'idSplit': self.split.id, 'startDate': '2026-01-01', 'isActive': True},
            format='json',
        ).data

        self.url = reverse('routines:my-routine-list')

    def test_create_routine(self):
        payload = {
            'idUserSplit': self.user_split['id'],
            'idSplitDay': self.day.id,
            'idExercise': self.exercise.id,
            'order': 1,
            'targetSets': 4,
            'targetReps': '8-12',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cannot_assign_day_from_different_split(self):
        other_split = make_split(name='Other')
        other_day = make_split_day(other_split, day_number=1, day_name='X')
        payload = {
            'idUserSplit': self.user_split['id'],
            'idSplitDay': other_day.id,
            'idExercise': self.exercise.id,
            'order': 1,
            'targetSets': 3,
            'targetReps': '5',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
