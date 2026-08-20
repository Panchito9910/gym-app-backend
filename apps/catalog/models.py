"""Catalog models: muscles, exercises, intensity techniques."""
from django.db import models

from apps.core.models import BaseModel


class Muscle(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    imgUrl = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'muscles'
        ordering = ['name']

    def __str__(self):
        return self.name


class Exercise(BaseModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    videoUrl = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'exercises'
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]

    def __str__(self):
        return self.name


class IntensityTechnique(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'intensity_techniques'
        ordering = ['name']

    def __str__(self):
        return self.name


class ExerciseMuscle(models.Model):
    """N:M between Exercise and Muscle with a role tag."""

    ROLE_PRIMARY = 'primary'
    ROLE_SECONDARY = 'secondary'
    ROLE_STABILIZER = 'stabilizer'
    ROLE_CHOICES = [
        (ROLE_PRIMARY, 'Primary'),
        (ROLE_SECONDARY, 'Secondary'),
        (ROLE_STABILIZER, 'Stabilizer'),
    ]

    id = models.BigAutoField(primary_key=True)
    idExercise = models.ForeignKey(
        Exercise, on_delete=models.CASCADE, related_name='muscles', db_column='idExercise'
    )
    idMuscle = models.ForeignKey(
        Muscle, on_delete=models.PROTECT, related_name='exercises', db_column='idMuscle'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_PRIMARY)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'exercise_muscles'
        unique_together = [('idExercise', 'idMuscle', 'role')]
        indexes = [
            models.Index(fields=['idExercise']),
            models.Index(fields=['idMuscle']),
        ]

    def __str__(self):
        return f'{self.idExercise.name} -> {self.idMuscle.name} ({self.role})'
