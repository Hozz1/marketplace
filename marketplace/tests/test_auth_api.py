from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from marketplace.models import UserProfile


class RegisterApiTest(APITestCase):
    def test_user_can_register_as_buyer(self):
        url = reverse('register')
        payload = {
            'username': 'buyer_test',
            'email': 'buyer_test@example.com',
            'password': 'strongpass123',
            'role': UserProfile.Role.BUYER,
        }

        response = self.client.post(
            url,
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(username='buyer_test').exists()
        )

        user = User.objects.get(username='buyer_test')

        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.role, UserProfile.Role.BUYER)
        self.assertNotIn('password', response.data)
        self.assertNotIn('role', response.data)


    def test_user_can_register_as_seller(self):
        url = reverse('register')
        payload = {
            'username': 'seller_test',
            'email': 'seller_test@example.com',
            'password': 'strongpass123',
            'role': UserProfile.Role.SELLER,
        }

        response = self.client.post(
            url,
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='seller_test')

        self.assertEqual(user.profile.role, UserProfile.Role.SELLER)


    def test_user_cannot_register_as_admin(self):
        url = reverse('register')

        payload = {
            'username': 'admin_test',
            'email': 'admin_test@example.com',
            'password': 'strongpass123',
            'role': UserProfile.Role.ADMIN,
        }

        response = self.client.post(
            url,
            payload,
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(
            User.objects.filter(username='admin_test').exists()
        )