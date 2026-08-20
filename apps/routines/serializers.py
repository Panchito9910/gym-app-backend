"""Routines serializers."""
from rest_framework import serializers

from apps.catalog.serializers import ExerciseSerializer

from .models import Routine


class RoutineSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(source='idExercise', read_only=True)
    exerciseName = serializers.CharField(source='idExercise.name', read_only=True)
    dayNumber = serializers.IntegerField(source='idSplitDay.dayNumber', read_only=True)
    dayName = serializers.CharField(source='idSplitDay.name', read_only=True)

    class Meta:
        model = Routine
        fields = [
            'id',
            'idUserSplit',
            'idSplitDay',
            'dayNumber',
            'dayName',
            'idExercise',
            'exerciseName',
            'exercise',
            'order',
            'targetSets',
            'targetReps',
            'status',
            'created',
            'updated',
        ]
        read_only_fields = ['id', 'created', 'updated', 'exerciseName', 'dayNumber', 'dayName', 'exercise']

    def validate(self, attrs):
        user_split = attrs.get('idUserSplit') or getattr(self.instance, 'idUserSplit', None)
        split_day = attrs.get('idSplitDay') or getattr(self.instance, 'idSplitDay', None)
        if user_split and split_day and split_day.idSplit_id != user_split.idSplit_id:
            raise serializers.ValidationError({'idSplitDay': 'Day does not belong to the user split.'})
        return attrs
