"""Workouts serializers."""
from rest_framework import serializers

from apps.catalog.serializers import IntensityTechniqueSerializer

from .models import Workout


class WorkoutSerializer(serializers.ModelSerializer):
    intensityTechnique = IntensityTechniqueSerializer(source='idIntensityTechnique', read_only=True)
    exerciseName = serializers.CharField(source='idRoutine.idExercise.name', read_only=True)
    dayNumber = serializers.IntegerField(source='idRoutine.idSplitDay.dayNumber', read_only=True)

    class Meta:
        model = Workout
        fields = [
            'id',
            'idRoutine',
            'idIntensityTechnique',
            'intensityTechnique',
            'exerciseName',
            'dayNumber',
            'workoutDate',
            'setNumber',
            'repetitions',
            'kg',
            'rpe',
            'notes',
            'status',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'created', 'updated', 'intensityTechnique', 'exerciseName', 'dayNumber', 'workoutDate']
