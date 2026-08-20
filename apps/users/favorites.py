"""User saved exercises (favorites)."""
from django.db import models

from apps.catalog.models import Exercise
from apps.core.models import BaseModel
from apps.users.models import User


class UserExercise(BaseModel):
    idUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='saved_exercises', db_column='idUser'
    )
    idExercise = models.ForeignKey(
        Exercise, on_delete=models.PROTECT, related_name='saved_by', db_column='idExercise'
    )

    class Meta:
        db_table = 'user_exercises'
        unique_together = [('idUser', 'idExercise')]
        indexes = [
            models.Index(fields=['idUser']),
            models.Index(fields=['idExercise']),
        ]

    def __str__(self):
        return f'{self.idUser.email} - {self.idExercise.name}'
