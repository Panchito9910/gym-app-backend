"""Workouts model: actual logged sets."""
from django.db import models

from apps.catalog.models import Exercise, IntensityTechnique
from apps.core.models import BaseModel
from apps.routines.models import Routine


class Workout(BaseModel):
    idRoutine = models.ForeignKey(
        Routine, on_delete=models.CASCADE, related_name='workouts', db_column='idRoutine'
    )
    idIntensityTechnique = models.ForeignKey(
        IntensityTechnique,
        on_delete=models.PROTECT,
        related_name='workouts',
        db_column='idIntensityTechnique',
        null=True,
        blank=True,
    )
    workoutDate = models.DateTimeField(auto_now_add=True)
    setNumber = models.PositiveSmallIntegerField()
    repetitions = models.PositiveSmallIntegerField()
    kg = models.DecimalField(max_digits=6, decimal_places=2)
    rpe = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    notes = models.CharField(max_length=500, blank=True)

    class Meta:
        db_table = 'workouts'
        ordering = ['-workoutDate']
        indexes = [
            models.Index(fields=['workoutDate']),
            models.Index(fields=['idRoutine']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(repetitions__gte=0), name='workout_repetitions_non_negative'
            ),
            models.CheckConstraint(condition=models.Q(kg__gte=0), name='workout_kg_non_negative'),
            models.CheckConstraint(
                condition=models.Q(setNumber__gt=0), name='workout_set_number_positive'
            ),
        ]

    def __str__(self):
        return f'{self.idRoutine.idExercise.name} - set {self.setNumber} ({self.kg}kg x{self.repetitions})'
