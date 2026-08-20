"""Routines views."""
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Routine
from .serializers import RoutineSerializer


class RoutineViewSet(viewsets.ModelViewSet):
    serializer_class = RoutineSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'created']
    ordering = ['idSplitDay', 'order']

    def get_queryset(self):
        user = self.request.user
        qs = Routine.objects.select_related('idExercise', 'idSplitDay', 'idUserSplit')
        if user.is_admin_role:
            return qs.all()
        return qs.filter(idUserSplit__idUser=user)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=False, methods=['get'], url_path='by-day')
    def by_day(self, request):
        day_id = request.query_params.get('dayId')
        if not day_id:
            return Response({'detail': 'dayId query param required.'}, status=400)
        qs = self.get_queryset().filter(idSplitDay_id=day_id)
        return Response(self.get_serializer(qs, many=True).data)
