"""Routines model: planned exercise per day in a user's active split."""
from django.core.exceptions import ValidationError
from django.db import models

from apps.catalog.models import Exercise
from apps.core.models import BaseModel
from apps.splits.models import SplitDay, UserSplit


class Routine(BaseModel):
    idUserSplit = models.ForeignKey(
        UserSplit, on_delete=models.CASCADE, related_name='routines', db_column='idUserSplit'
    )
    idSplitDay = models.ForeignKey(
        SplitDay, on_delete=models.PROTECT, related_name='routines', db_column='idSplitDay'
    )
    idExercise = models.ForeignKey(
        Exercise, on_delete=models.PROTECT, related_name='routine_entries', db_column='idExercise'
    )
    order = models.PositiveSmallIntegerField(default=1)
    targetSets = models.PositiveSmallIntegerField()
    targetReps = models.CharField(max_length=15, help_text='e.g. "8-12", "5", "AMRAP"')

    class Meta:
        db_table = 'routines'
        ordering = ['idUserSplit', 'idSplitDay', 'order']
        indexes = [
            models.Index(fields=['idUserSplit']),
            models.Index(fields=['idSplitDay']),
            models.Index(fields=['idExercise']),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(targetSets__gt=0), name='routine_target_sets_positive'
            )
        ]

    def clean(self):
        if self.idUserSplit_id and self.idSplitDay_id:
            if self.idSplitDay.idSplit_id != self.idUserSplit.idSplit_id:
                raise ValidationError(
                    {'idSplitDay': 'Day does not belong to the user split.'}
                )

    def __str__(self):
        return f'{self.idExercise.name} (Day {self.idSplitDay.dayNumber})'
