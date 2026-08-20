"""Workouts tests."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.core.test_factories import (
    make_exercise,
    make_muscle,
    make_split,
    make_split_day,
    make_technique,
    make_user,
)


class WorkoutTests(APITestCase):
    def setUp(self):
        self.user = make_user(email='workout@example.com', user_name='workoutuser')
        self.split = make_split()
        self.day = make_split_day(self.split)
        self.muscle = make_muscle()
        self.exercise = make_exercise(muscle=self.muscle)
        self.technique = make_technique()

        self.client.force_authenticate(user=self.user)
        split_resp = self.client.post(
            reverse('splits:my-split-list'),
            {'idSplit': self.split.id, 'startDate': '2026-01-01', 'isActive': True},
            format='json',
        ).data
        routine_resp = self.client.post(
            reverse('routines:my-routine-list'),
            {
                'idUserSplit': split_resp['id'],
                'idSplitDay': self.day.id,
                'idExercise': self.exercise.id,
                'order': 1,
                'targetSets': 4,
                'targetReps': '8-12',
            },
            format='json',
        ).data
        self.routine_id = routine_resp['id']
        self.url = reverse('workouts:workout-list')

    def test_create_workout(self):
        payload = {
            'idRoutine': self.routine_id,
            'idIntensityTechnique': self.technique.id,
            'setNumber': 1,
            'repetitions': 10,
            'kg': '60.00',
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['exerciseName'], self.exercise.name)

    def test_stats_endpoint(self):
        self.client.post(
            self.url,
            {
                'idRoutine': self.routine_id,
                'setNumber': 1,
                'repetitions': 10,
                'kg': '60.00',
            },
            format='json',
        )
        self.client.post(
            self.url,
            {
                'idRoutine': self.routine_id,
                'setNumber': 2,
                'repetitions': 8,
                'kg': '62.50',
            },
            format='json',
        )
        response = self.client.get(reverse('workouts:workout-stats'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['byExercise']), 1)
        self.assertEqual(response.data['byExercise'][0]['totalSets'], 2)
