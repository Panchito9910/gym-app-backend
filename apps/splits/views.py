"""Splits views."""
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdminOrTrainer, IsAdmin
from apps.users.models import User

from .models import Split, SplitDay, UserSplit
from .serializers import SplitDaySerializer, SplitSerializer, UserSplitSerializer


class SplitViewSet(viewsets.ModelViewSet):
    queryset = Split.objects.prefetch_related('days').all()
    serializer_class = SplitSerializer

    def get_permissions(self):
        if self.action in {'list', 'retrieve'}:
            return [IsAuthenticated()]
        return [IsAdmin()]

    @action(detail=True, methods=['get', 'post'], url_path='days')
    def days(self, request, pk=None):
        split = self.get_object()
        if request.method == 'GET':
            qs = split.days.all()
            return Response(SplitDaySerializer(qs, many=True).data)
        if not (request.user.is_admin_role or request.user.is_trainer_role):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = SplitDaySerializer(data={**request.data, 'idSplit': split.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['patch', 'delete'], url_path='days/(?P<day_id>[^/.]+)')
    def day_detail(self, request, pk=None, day_id=None):
        if not (request.user.is_admin_role or request.user.is_trainer_role):
            return Response({'detail': 'Forbidden.'}, status=status.HTTP_403_FORBIDDEN)
        day = get_object_or_404(SplitDay, pk=day_id, idSplit_id=pk)
        if request.method == 'DELETE':
            day.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer = SplitDaySerializer(day, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserSplitViewSet(viewsets.ModelViewSet):
    serializer_class = UserSplitSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin_role:
            return UserSplit.objects.select_related('idUser', 'idSplit').all()
        return UserSplit.objects.select_related('idSplit').filter(idUser=user)

    def perform_create(self, serializer):
        serializer.save(idUser=self.request.user)

    @action(detail=False, methods=['get'])
    def active(self, request):
        qs = self.get_queryset().filter(isActive=True)
        if not qs.exists():
            return Response({'detail': 'No active split.'}, status=status.HTTP_404_NOT_FOUND)
        return Response(self.get_serializer(qs.first()).data)
