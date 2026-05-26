from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rest_framework import generics, mixins, permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Category, Order, Product, UserProfile
from .permissions import IsOwnerOrAdmin, IsSeller, IsBuyer
from .serializers import CategorySerializer, ProductSerializer, RegisterSerializer, OrderSerializer


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


class OrderViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.select_related(
            'buyer',
            'product',
        )

        user = self.request.user

        if not user.is_authenticated:
            return Order.objects.none()

        if self._is_admin(user):
            return queryset

        return queryset.filter(buyer=user)

    def get_permissions(self):
        if self.action == 'create':
            return (IsBuyer(),)

        return (permissions.IsAuthenticated(),)

    def perform_create(self, serializer):
        user = self.request.user
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        with transaction.atomic():
            product = Product.objects.select_for_update().get(
                pk=product.pk,
            )

            if not product.is_available:
                return ValidationError(
                    'Товар недоступен для заказа.'
                )

            if quantity > product.quantity:
                raise ValidationError(
                    'Недостаточно товара на складе.'
                )

            total_price = product.price * quantity

            serializer.save(
                buyer=user,
                product=product,
                total_price=total_price,
            )

            product.quantity -= quantity

            if product.quantity == 0:
                product.is_available = False

            product.save(
                update_fields=(
                    'quantity',
                    'is_available',
                    'updated_at',
                )
            )

    @staticmethod
    def _is_admin(user):
        return (
            hasattr(user, 'profile')
            and user.profile.role == UserProfile.Role.ADMIN
        )
