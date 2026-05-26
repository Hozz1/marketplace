from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from .models import Category, Product, UserProfile
from .permissions import IsOwnerOrAdmin, IsSeller
from .serializers import CategorySerializer, ProductSerializer, RegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'category',
            'seller',
        )

        user = self.request.user

        if self.action == 'list':
            return queryset.filter(is_available=True)

        if self.action == 'retrieve':
            if not user.is_authenticated:
                return queryset.filter(is_available=True)

            if self._is_admin(user):
                return queryset

            return queryset.filter(
                Q(is_available=True) | Q(seller=user)
            )

        return queryset

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return (permissions.AllowAny(),)

        if self.action == 'create':
            return (IsSeller(),)

        return (IsOwnerOrAdmin(),)

    def perform_create(self, serializer):
        user = self.request.user

        if not hasattr(user, 'profile'):
            raise PermissionDenied(
                'У пользователя отсутствует профиль.'
            )

        if user.profile.role != UserProfile.Role.SELLER:
            raise PermissionDenied(
                'Создавать товары может только продавец.'
            )

        serializer.save(seller=user)

    @staticmethod
    def _is_admin(user):
        return (
            hasattr(user, 'profile')
            and user.profile.role == UserProfile.Role.ADMIN
        )