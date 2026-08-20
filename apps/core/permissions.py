"""Reusable DRF permissions."""
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrTrainer(BasePermission):
    """Read for any authenticated user; write for admin or trainer."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return getattr(request.user, 'is_admin_or_trainer', False)


class IsAdmin(BasePermission):
    """Allow only users with the `admin` role."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, 'is_admin_role', False)
        )


class IsOwnerOrReadOnly(BasePermission):
    """Object-level: only the owner (or admin) can edit."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        owner = getattr(obj, 'idUser', None) or getattr(obj, 'user', None)
        if owner is None:
            return False
        if getattr(request.user, 'is_admin_role', False):
            return True
        return owner == request.user
