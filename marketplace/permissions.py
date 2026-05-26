from rest_framework import permissions

from .models import UserProfile


class IsSeller(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and hasattr(request.user, 'profile')
                and request.user.profile.role == UserProfile.Role.SELLER
        )


class IsAdminRole(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
                request.user.is_authenticated
                and hasattr(request.user, 'profile')
                and request.user.profile.role == UserProfile.Role.ADMIN
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        if hasattr(request.user, 'profile'):
            if request.user.profile.role == UserProfile.Role.ADMIN:
                return True

        return obj.seller == request.user


class IsBuyer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == UserProfile.Role.BUYER
        )
