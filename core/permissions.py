from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admin role can access."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsAnalystOrAdmin(BasePermission):
    """Analyst and admin can access."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role in ['admin', 'analyst']
        )


class IsAnyRole(BasePermission):
    """Any authenticated user (viewer, analyst, admin) can access."""
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated
        )