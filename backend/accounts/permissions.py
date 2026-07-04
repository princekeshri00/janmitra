from rest_framework.permissions import BasePermission

from .models import UserRole


class IsClient(BasePermission):
    message = "Client access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.CLIENT
        )


class IsManagement(BasePermission):
    message = "Management access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.MANAGEMENT
        )


class IsMP(BasePermission):
    message = "MP access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.MP
        )


class IsAdminRole(BasePermission):
    message = "Admin access is required."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsClientOrAdmin(BasePermission):
    message = "Client or admin access is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in {
            UserRole.CLIENT,
            UserRole.ADMIN,
        }


class IsManagementOrAdmin(BasePermission):
    message = "Management or admin access is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in {
            UserRole.MANAGEMENT,
            UserRole.ADMIN,
        }


class IsMPOrAdmin(BasePermission):
    message = "MP or admin access is required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return request.user.role in {
            UserRole.MP,
            UserRole.ADMIN,
        }