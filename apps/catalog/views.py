"""Catalog viewsets."""
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrTrainer

from .models import Exercise, ExerciseMuscle, IntensityTechnique, Muscle
from .serializers import (
    ExerciseMuscleSerializer,
    ExerciseSerializer,
    IntensityTechniqueSerializer,
    MuscleSerializer,
)


class MuscleViewSet(viewsets.ModelViewSet):
    queryset = Muscle.objects.all()
    serializer_class = MuscleSerializer
    permission_classes = [IsAdminOrTrainer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created']
    ordering = ['name']


class IntensityTechniqueViewSet(viewsets.ModelViewSet):
    queryset = IntensityTechnique.objects.all()
    serializer_class = IntensityTechniqueSerializer
    permission_classes = [IsAdminOrTrainer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering = ['name']


class ExerciseViewSet(viewsets.ModelViewSet):
    queryset = Exercise.objects.prefetch_related('muscles__idMuscle').all()
    serializer_class = ExerciseSerializer
    permission_classes = [IsAdminOrTrainer]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created']
    ordering = ['name']

    @action(detail=True, methods=['get'])
    def muscles(self, request, pk=None):
        exercise = self.get_object()
        serializer = ExerciseMuscleSerializer(exercise.muscles.all(), many=True)
        return Response(serializer.data)
