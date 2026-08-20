"""Favorites serializers and viewset."""
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.catalog.serializers import ExerciseSerializer

from .favorites import UserExercise
from .models import User


class UserExerciseViewSet(viewsets.ModelViewSet):
    """CRUD for the current user's saved exercises."""

    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user: User = self.request.user
        if user.is_admin_role:
            return UserExercise.objects.select_related('idExercise').all()
        return UserExercise.objects.filter(idUser=user).select_related('idExercise')

    def get_serializer_class(self):
        from rest_framework import serializers

        class _Serializer(serializers.ModelSerializer):
            exercise = ExerciseSerializer(source='idExercise', read_only=True)
            exerciseId = serializers.IntegerField(source='idExercise.id', read_only=True)
            exerciseName = serializers.CharField(source='idExercise.name', read_only=True)

            class Meta:
                model = UserExercise
                fields = ['id', 'idUser', 'exerciseId', 'exerciseName', 'exercise', 'created']
                read_only_fields = ['id', 'idUser', 'exerciseId', 'exerciseName', 'exercise', 'created']

        return _Serializer

    def perform_create(self, serializer):
        exercise = serializer.validated_data['idExercise']
        UserExercise.objects.get_or_create(idUser=self.request.user, idExercise=exercise)
