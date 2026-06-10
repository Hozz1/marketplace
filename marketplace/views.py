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

from .roles import is_admin_user

from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiTypes,
    extend_schema,
    extend_schema_view,
)

PRODUCT_LIST_PARAMETERS = [
    OpenApiParameter(
        name='search',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='Search by product title or description.',
    ),
    OpenApiParameter(
        name='category',
        type=OpenApiTypes.INT,
        location=OpenApiParameter.QUERY,
        description='Filter products by category id.',
    ),
    OpenApiParameter(
        name='min_price',
        type=OpenApiTypes.DECIMAL,
        location=OpenApiParameter.QUERY,
        description='Filter products with price greater than or equal to this value.',
    ),
    OpenApiParameter(
        name='max_price',
        type=OpenApiTypes.DECIMAL,
        location=OpenApiParameter.QUERY,
        description='Filter products with price less than or equal to this value.',
    ),
    OpenApiParameter(
        name='ordering',
        type=OpenApiTypes.STR,
        location=OpenApiParameter.QUERY,
        description='Order products by price, -price, created_at or -created_at.',
    ),
]

@extend_schema(
    tags=['Auth'],
    summary='Register a new user',
    description=(
        'Creates a new user account and related UserProfile. '
        'Public registration allows only buyer and seller roles.'
    ),
    request=RegisterSerializer,
    responses={201: RegisterSerializer},
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

@extend_schema_view(
    list=extend_schema(
        tags=['Categories'],
        summary='Get category list',
        description='Returns a list of product categories.',
    ),
    retrieve=extend_schema(
        tags=['Categories'],
        summary='Get category details',
        description='Returns details of a single category.',
    ),
)
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


@extend_schema_view(
    list=extend_schema(
        tags=['Products'],
        summary='Get product list',
        description=(
            'Returns available products with cursor pagination. '
            'Supports search, category filter, price range filter and ordering.'
        ),
        parameters=PRODUCT_LIST_PARAMETERS,
    ),
    retrieve=extend_schema(
        tags=['Products'],
        summary='Get product details',
        description='Returns details of a single product.',
    ),
    create=extend_schema(
        tags=['Products'],
        summary='Create product',
        description='Creates a product. Available only for users with seller role.',
    ),
    update=extend_schema(
        tags=['Products'],
        summary='Update product',
        description='Fully updates a product. Available only for owner or admin.',
    ),
    partial_update=extend_schema(
        tags=['Products'],
        summary='Partially update product',
        description='Partially updates a product. Available only for owner or admin.',
    ),
    destroy=extend_schema(
        tags=['Products'],
        summary='Delete product',
        description='Deletes a product. Available only for owner or admin.',
    ),
)
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

            if is_admin_user(user):
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


@extend_schema_view(
    list=extend_schema(
        tags=['Orders'],
        summary='Get order list',
        description=(
            'Returns user orders. Admin users can see all orders; '
            'regular users can see only their own orders.'
        ),
    ),
    retrieve=extend_schema(
        tags=['Orders'],
        summary='Get order details',
        description='Returns details of a single order available to the current user.',
    ),
    create=extend_schema(
        tags=['Orders'],
        summary='Create order',
        description=(
            'Creates an order for the authenticated buyer. '
            'The backend calculates total_price and decreases product quantity.'
        ),
        request=OrderSerializer,
        responses={201: OrderSerializer},
    ),
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

        if is_admin_user(user):
            return queryset

        return queryset.filter(buyer=user)

    def get_permissions(self):
        if self.action == 'create':
            return (IsBuyer(),)

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
