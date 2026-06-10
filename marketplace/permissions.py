from rest_framework import permissions

from .models import UserProfile

from .roles import is_admin_user, is_buyer_user, is_seller_user


class IsBuyer(permissions.BasePermission):
    message = 'Доступ разрешён только покупателям.'

    def has_permission(self, request, view):
        return is_buyer_user(request.user)

class IsSeller(permissions.BasePermission):
    message = 'Доступ разрешен только продавцам.'

    def has_permission(self, request, view):
        return is_seller_user(request.user)


class IsAdminRole(permissions.BasePermission):
    message = 'Доступ разрешен только администраторам.'

    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    message = 'Доступ разрешен только владельцу или администратору.'

    def has_object_permission(self, request, view, obj):
        if is_admin_user(request.user):
            return True

        return getattr(obj, 'seller_id', None) == request.user.id
