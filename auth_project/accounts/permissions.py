from rest_framework import permissions
from django.contrib.auth import get_user_model
from .models import UserRole, RolePermission

User = get_user_model()


class HasPermission(permissions.BasePermission):

    def __init__(self, resource_type=None, action=None):
        self.resource_type = resource_type
        self.action = action

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        if self.resource_type and self.action:
            return self._check_permission(
                request.user, self.resource_type, self.action)

        return True

    def has_object_permission(self, request, view, obj):
        user = request.user

        if user.is_superuser:
            return True

        if hasattr(obj, 'user') and obj.user == user:
            return True
        if hasattr(obj, 'id') and obj == user:
            return True

        return self._check_permission(user, self.resource_type, self.action)

    def _check_permission(self, user, resource_type, action):

        user_roles = UserRole.objects.filter(user=user).select_related('role')

        for user_role in user_roles:
            if RolePermission.objects.filter(
                    role=user_role.role,
                    permission__resource_type=resource_type,
                    permission__action=action
            ).exists():
                return True

        return False


class IsAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['admin', 'super_admin']
        ).exists()


class IsSuperAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        return UserRole.objects.filter(
            user=request.user,
            role__name='super_admin'
        ).exists()


class IsManager(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True

        return UserRole.objects.filter(
            user=request.user,
            role__name__in=['admin', 'super_admin', 'manager']
        ).exists()


class IsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):

        if hasattr(obj, 'id') and obj == request.user:
            return True

        if hasattr(obj, 'user') and obj.user == request.user:
            return True

        if hasattr(obj, 'owner') and obj.owner == request.user:
            return True

        return IsAdmin().has_permission(request, view)
