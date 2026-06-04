from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketplace.models import Category, Order, Product, UserProfile


class OrderApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Ceramics',
            description='Handmade ceramic products',
        )

        self.seller = User.objects.create_user(
            username='seller_test',
            email='seller_test@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.seller,
            role=UserProfile.Role.SELLER,
        )

        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.buyer,
            role=UserProfile.Role.BUYER,
        )

        self.other_buyer = User.objects.create_user(
            username='other_buyer',
            email='other_buyer@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.other_buyer,
            role=UserProfile.Role.BUYER,
        )

        self.admin = User.objects.create_user(
            username='admin_test',
            email='admin_test@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.admin,
            role=UserProfile.Role.ADMIN,
        )

        self.product = Product.objects.create(
            title='Ceramic mug',
            description='Handmade mug.',
            price=Decimal('1200.00'),
            quantity=5,
            category=self.category,
            seller=self.seller,
        )

    def test_buyer_can_create_order(self):
        url = reverse('order-list')
        payload = {
            'product': self.product.id,
            'quantity': 2,
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.get()

        self.assertEqual(order.buyer, self.buyer)
        self.assertEqual(order.product, self.product)
        self.assertEqual(order.quantity, 2)
        self.assertEqual(order.total_price, Decimal('2400.00'))

    def test_product_quantity_decreases_after_order(self):
        url = reverse('order-list')
        payload = {
            'product': self.product.id,
            'quantity': 2,
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 3)
        self.assertTrue(self.product.is_available)

    def test_product_becomes_unavailable_when_quantity_becomes_zero(self):
        url = reverse('order-list')
        payload = {
            'product': self.product.id,
            'quantity': 5,
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 0)
        self.assertFalse(self.product.is_available)

    def test_buyer_cannot_order_more_than_available_quantity(self):
        url = reverse('order-list')
        payload = {
            'product': self.product.id,
            'quantity': 999,
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

        self.product.refresh_from_db()

        self.assertEqual(self.product.quantity, 5)

    def test_seller_cannot_create_order(self):
        url = reverse('order-list')
        payload = {
            'product': self.product.id,
            'quantity': 1,
        }

        self.client.force_authenticate(user=self.seller)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Order.objects.count(), 0)

    def test_buyer_sees_only_own_orders(self):
        buyer_order = Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=1,
            total_price=Decimal('1200.00'),
        )
        Order.objects.create(
            buyer=self.other_buyer,
            product=self.product,
            quantity=1,
            total_price=Decimal('1200.00'),
        )

        url = reverse('order-list')

        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], buyer_order.id)

    def test_admin_sees_all_orders(self):
        Order.objects.create(
            buyer=self.buyer,
            product=self.product,
            quantity=1,
            total_price=Decimal('1200.00'),
        )

        Order.objects.create(
            buyer=self.other_buyer,
            product=self.product,
            quantity=1,
            total_price=Decimal('1200.00'),
        )

        url = reverse('order-list')

        self.client.force_authenticate(user=self.admin)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
