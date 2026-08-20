"""Abstract base model with timestamp and status fields."""
from django.db import models


class BaseModel(models.Model):
    """Common fields for every business entity."""

    status = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
