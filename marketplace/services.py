from django.db import transaction

from .models import Order, Product


class OrderCreationError(Exception):
    pass


class OrderStatusUpdateError(Exception):
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


def update_order_status(*, order, new_status):
    allowed_transitions = {
        Order.Status.CREATED: {
            Order.Status.PAID,
            Order.Status.CANCELLED,
        },
        Order.Status.PAID: {
            Order.Status.COMPLETED,
        },
        Order.Status.CANCELLED: set(),
        Order.Status.COMPLETED: set(),
    }

    with transaction.atomic():
        try:
            locked_order = (
                Order.objects
                .select_for_update()
                .select_related('product')
                .get(pk=order.pk)
            )
        except Order.DoesNotExist as error:
            raise OrderStatusUpdateError(
                'Заказ не найден.'
            ) from error

        if locked_order.status == new_status:
            return locked_order

        available_statuses = allowed_transitions[locked_order.status]

        if new_status not in available_statuses:
            raise OrderStatusUpdateError(
                'Недопустимый переход статуса заказа.'
            )

        if new_status == Order.Status.CANCELLED:
            product = Product.objects.select_for_update().get(
                pk=locked_order.product_id,
            )

            product.quantity += locked_order.quantity

            if product.quantity > 0:
                product.is_available = True

            product.save(
                update_fields=(
                    'quantity',
                    'is_available',
                    'updated_at',
                )
            )

        locked_order.status = new_status
        locked_order.save(update_fields=('status',))

    return locked_order
