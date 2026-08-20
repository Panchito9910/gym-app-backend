"""Catalog serializers."""
from rest_framework import serializers

from .models import Exercise, ExerciseMuscle, IntensityTechnique, Muscle


class MuscleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muscle
        fields = ['id', 'name', 'imgUrl', 'description', 'status', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']


class IntensityTechniqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntensityTechnique
        fields = ['id', 'name', 'description', 'status', 'created', 'updated']
        read_only_fields = ['id', 'created', 'updated']


class ExerciseMuscleSerializer(serializers.ModelSerializer):
    muscleName = serializers.CharField(source='idMuscle.name', read_only=True)

    class Meta:
        model = ExerciseMuscle
        fields = ['id', 'idMuscle', 'muscleName', 'role']
        read_only_fields = ['id']


class ExerciseSerializer(serializers.ModelSerializer):
    muscles = ExerciseMuscleSerializer(source='muscles.all', many=True, read_only=True)
    muscleIds = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text='List of muscle IDs to link to this exercise.',
    )

    class Meta:
        model = Exercise
        fields = [
            'id',
            'name',
            'description',
            'videoUrl',
            'status',
            'created',
            'updated',
            'muscles',
            'muscleIds',
        ]
        read_only_fields = ['id', 'created', 'updated']

    def create(self, validated_data):
        muscle_ids = validated_data.pop('muscleIds', [])
        exercise = Exercise.objects.create(**validated_data)
        for muscle_id in muscle_ids:
            ExerciseMuscle.objects.get_or_create(
                idExercise=exercise, idMuscle_id=muscle_id, defaults={'role': 'primary'}
            )
        return exercise

    def update(self, instance, validated_data):
        muscle_ids = validated_data.pop('muscleIds', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if muscle_ids is not None:
            instance.muscles.all().delete()
            for muscle_id in muscle_ids:
                ExerciseMuscle.objects.create(
                    idExercise=instance, idMuscle_id=muscle_id, role='primary'
                )
        return instance
