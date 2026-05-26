from django.db import transaction

from .models import Order, Product


class OrderCreationError(Exception):
    pass


def create_order(*, buyer, product, quantity):
    if quantity <= 0:
        raise OrderCreationError(
            'Количество товара должно быть больше нуля.'
        )

    with transaction.atomic():
        try:
            locked_product = Product.objects.select_for_update().get(
               pk=product.pk,
            )
        except Product.DoesNotExist as error:
            raise OrderCreationError(
                'Товар не найден.'
            )from error

        if not locked_product.is_available:
            raise OrderCreationError(
                'Товар недоступен для заказа.'
            )

        if quantity > locked_product.quantity:
            raise OrderCreationError(
                'Недостаточно товара на складе.'
            )

        total_price = locked_product.price * quantity

        order = Order.objects.create(
            buyer=buyer,
            product=locked_product,
            quantity=quantity,
            total_price=total_price,
        )

        locked_product.quantity -= quantity

        if locked_product.quantity == 0:
            locked_product.is_available = False

        locked_product.save(
            update_fields=(
                'quantity',
                'is_available',
                'updated_at',
            )
        )

    return order

