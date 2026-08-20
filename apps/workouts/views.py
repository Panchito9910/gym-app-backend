"""Workouts views."""
from django.db.models import Count, Sum
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Workout
from .serializers import WorkoutSerializer


class WorkoutViewSet(viewsets.ModelViewSet):
    serializer_class = WorkoutSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['workoutDate', 'setNumber']
    ordering = ['-workoutDate']

    def get_queryset(self):
        user = self.request.user
        qs = Workout.objects.select_related(
            'idRoutine__idExercise', 'idRoutine__idSplitDay', 'idRoutine__idUserSplit', 'idIntensityTechnique'
        )
        if user.is_admin_role:
            return qs.all()
        return qs.filter(idRoutine__idUserSplit__idUser=user)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        qs = self.get_queryset()
        routine_id = request.query_params.get('routineId')
        if routine_id:
            qs = qs.filter(idRoutine_id=routine_id)

        by_exercise = (
            qs.values('idRoutine__idExercise__id', 'idRoutine__idExercise__name')
            .annotate(totalSets=Count('id'), totalReps=Sum('repetitions'), totalVolume=Sum('kg'))
            .order_by('-totalVolume')
        )
        return Response({'byExercise': list(by_exercise)})
