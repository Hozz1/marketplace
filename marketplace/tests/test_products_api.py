from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketplace.models import Category, Product, UserProfile


class ProductApiTests(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Ceramics',
            description='Handmade ceramic products.',
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

        self.other_seller = User.objects.create_user(
            username='other_seller',
            email='other_seller@example.com',
            password='strongpass123',
        )

        UserProfile.objects.create(
            user=self.other_seller,
            role=UserProfile.Role.SELLER,
        )

        self.buyer = User.objects.create_user(
            username='buyer_test',
            email='buyer_test@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.buyer,
            role=UserProfile.Role.BUYER,
        )

        self.product = Product.objects.create(
            title='Ceramic mug',
            description='Handmade mug.',
            price='1200.00',
            quantity=5,
            category=self.category,
            seller=self.seller,
        )

    def test_anonymous_user_can_view_products(self):
        url = reverse('product-list')

        response = (
            self.client.get(url)
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_seller_can_create_product(self):
        url = reverse('product-list')
        payload = {
            'title': 'Wooden spoon',
            'description': 'Handmade wooden spoon.',
            'price': '500.00',
            'quantity': 10,
            'category': self.category.id,
        }

        self.client.force_authenticate(user=self.seller)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        product = Product.objects.get(title='Wooden spoon')

        self.assertEqual(product.seller, self.seller)
        self.assertEqual(product.category, self.category)

    def test_buyer_cannot_create_product(self):
        url = reverse('product-list')
        payload = {
            'title': 'Buyer product',
            'description': 'This should not be created.',
            'price': '700.00',
            'quantity': 3,
            'category': self.category.id,
        }

        self.client.force_authenticate(user=self.buyer)
        response = self.client.post(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(
            Product.objects.filter(title='Buyer product').exists()
        )

    def test_seller_cannot_update_another_seller_product(self):
        url = reverse(
            'product-detail',
            kwargs={'pk': self.product.pk},
        )
        payload = {
            'title': 'Hacked title',
        }

        self.client.force_authenticate(user=self.other_seller)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, 'Ceramic mug')

    def test_owner_can_update_own_product(self):
        url = reverse(
            'product-detail',
            kwargs={'pk': self.product.pk},
        )
        payload = {
            'title': 'Updated ceramic mug',
        }

        self.client.force_authenticate(user=self.seller)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.title, 'Updated ceramic mug')
