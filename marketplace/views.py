from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import Category, Order, Product, UserProfile
from .permissions import IsOwnerOrAdmin, IsSeller, IsBuyer
from .serializers import CategorySerializer, ProductSerializer, RegisterSerializer, OrderSerializer
from .services import OrderCreationError, create_order

from .pagination import ProductCursorPagination

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
    pagination_class = ProductCursorPagination

    def get_queryset(self):
        queryset = Product.objects.select_related(
            'category',
            'seller',
        )

        user = self.request.user

        if self.action == 'list':
            queryset = queryset.filter(is_available=True)
            return self._apply_product_filters(queryset)

        if self.action == 'retrieve':
            if not user.is_authenticated:
                return queryset.filter(is_available=True)

            if self._is_admin(user):
                return queryset

            return queryset.filter(
                Q(is_available=True) | Q(seller=user)
            )

        return queryset

    def _apply_product_filters(self, queryset):
        search = self.request.query_params.get('search')
        category = self.request.query_params.get('category')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
            )

        if category:
            queryset = queryset.filter(category_id=category)

        if min_price:
            queryset = queryset.filter(price__gte=min_price)

        if max_price:
            queryset = queryset.filter(price__lte=max_price)

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
            return(IsBuyer(),)

        return (permissions.IsAuthenticated(),)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            order = create_order(
                buyer=request.user,
                product=serializer.validated_data['product'],
                quantity=serializer.validated_data['quantity'],
            )
        except OrderCreationError as error:
            raise ValidationError(str(error)) from error

        response_serializer = self.get_serializer(order)

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _is_admin(user):
        return (
            hasattr(user, 'profile')
            and user.profile.role == UserProfile.Role.ADMIN
        )
