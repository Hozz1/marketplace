from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    class Role(models.TextChoices):
        BUYER = 'buyer', 'Покупатель'
        SELLER = 'seller', 'Продавец'
        ADMIN = 'admin', 'Администратор'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BUYER
    )

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = 'created', 'Создан'
        PAID = 'paid', 'Оплачен'
        CANCELLED = 'cancelled', 'Отменён'
        COMPLETED = 'completed', 'Завершен'

    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='orders',
    )
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.CREATED,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Заказ #{self.id} - {self.buyer.username}'
