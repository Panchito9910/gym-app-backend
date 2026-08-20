"""User views."""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.core.permissions import IsAdmin

from .models import Role, User
from .serializers import (
    ChangePasswordSerializer,
    RoleSerializer,
    UserSerializer,
)


class RoleViewSet(viewsets.ModelViewSet):
    """CRUD for roles. Only admins."""

    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAdmin]


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only listing for admin. Users get /me/ via the action."""

    queryset = User.objects.select_related('idRole').all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(idRole__name=role)
        return qs

    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            return Response(UserSerializer(request.user).data)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='me/change-password',
    )
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['newPassword'])
        request.user.save()
        return Response({'detail': 'Password updated.'}, status=status.HTTP_200_OK)
