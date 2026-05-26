from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Category, Order, Product, UserProfile


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'description',
        )


class ProductSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(
        source='seller.username',
        read_only=True
    )
    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'description',
            'price',
            'quantity',
            'image',
            'category',
            'category_name',
            'seller',
            'seller_username',
            'created_at',
            'updated_at',
            'is_available',
        )
        read_only_fields = (
            'seller',
            'created_at',
            'updated_at',
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Цена товара должна быть больше нуля.'
            )
        return value

    def validate(self, attrs):
        quantity = attrs.get(
            'quantity',
            self.instance.quantity if self.instance else None,
        )
        is_available = attrs.get(
            'is_available',
            self.instance.is_available if self.instance else True,
        )

        if is_available and quantity == 0:
            raise serializers.ValidationError(
                'Товар с нулевым количеством не может быть доступен.'
            )

        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(
        choices=(
            (UserProfile.Role.BUYER, 'Покупатель'),
            (UserProfile.Role.SELLER, 'Продавец'),
        ),
        default=UserProfile.Role.BUYER,
        write_only=True,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'password',
            'role',
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {
                'required': True,
                'allow_blank': False,
            },
        }

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует.'
            )

        return value

    def create(self, validated_data):
        role = validated_data.pop('role', UserProfile.Role.BUYER)
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        UserProfile.objects.create(
            user=user,
            role=role
        )

        return user


class OrderSerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(
        source='buyer.username',
        read_only=True,
    )
    product_title = serializers.CharField(
        source='product.title',
        read_only=True
    )

    class Meta:
        model = Order
        fields = (
            'id',
            'buyer',
            'buyer_username',
            'product',
            'product_title',
            'quantity',
            'total_price',
            'status',
            'created_at',
        )
        read_only_fields = (
            'buyer',
            'total_price',
            'status',
            'created_at',
        )

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Количество товара дожно быть больше нуля.'
            )

        return value

    def validate(self, attrs):
        product = attrs.get('product')
        quantity = attrs.get('quantity')

        if product is None or quantity is None:
            return attrs

        if not product.is_available:
            raise serializers.ValidationError(
                'Товар недоступен для заказа.'
            )

        if quantity > product.quantity:
            raise serializers.ValidationError(
                'Недостаточно товара на складе.'
            )

        return attrs
