from django.contrib import admin

from .models import Category, Order, Product, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'price',
        'quantity',
        'category',
        'seller',
        'is_available',
        'created_at',
    )
    list_filter = ('category', 'is_available', 'created_at')
    search_fields = ('title', 'description', 'seller__username')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'buyer',
        'product',
        'quantity',
        'total_price',
        'status',
        'created_at',
    )
    list_filter = ('status', 'created_at')
    search_fields = ('buyer__username', 'product__title')
