"""Splits models: global templates and per-user adoption."""
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel
from apps.users.models import User


class Split(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'splits'
        ordering = ['name']
        verbose_name_plural = 'splits'

    def __str__(self):
        return self.name


class SplitDay(BaseModel):
    idSplit = models.ForeignKey(
        Split, on_delete=models.CASCADE, related_name='days', db_column='idSplit'
    )
    dayNumber = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=80)

    class Meta:
        db_table = 'split_days'
        ordering = ['idSplit', 'dayNumber']
        unique_together = [('idSplit', 'dayNumber')]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(dayNumber__gte=1) & models.Q(dayNumber__lte=7),
                name='split_day_number_range',
            )
        ]

    def __str__(self):
        return f'{self.idSplit.name} - Day {self.dayNumber}: {self.name}'


class UserSplit(BaseModel):
    idUser = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_splits', db_column='idUser'
    )
    idSplit = models.ForeignKey(
        Split, on_delete=models.PROTECT, related_name='adopters', db_column='idSplit'
    )
    startDate = models.DateField()
    endDate = models.DateField(null=True, blank=True)
    isActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_splits'
        ordering = ['-startDate']
        indexes = [
            models.Index(fields=['idUser', 'isActive']),
            models.Index(fields=['idSplit']),
        ]

    def clean(self):
        if self.endDate and self.endDate < self.startDate:
            raise ValidationError({'endDate': 'endDate must be after startDate.'})

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.isActive:
            UserSplit.objects.filter(idUser=self.idUser).exclude(pk=self.pk).update(
                isActive=False, status=False
            )

    def __str__(self):
        return f'{self.idUser.email} - {self.idSplit.name}'
