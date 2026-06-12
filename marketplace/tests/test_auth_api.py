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


class MeApiTests(APITestCase):
    def setUp(self):
        self.buyer = User.objects.create_user(
            username='buyer_me',
            email='buyer_me@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.buyer,
            role=UserProfile.Role.BUYER,
        )

        self.seller = User.objects.create_user(
            username='seller_me',
            email='seller_me@example.com',
            password='strongpass123',
        )
        UserProfile.objects.create(
            user=self.seller,
            role=UserProfile.Role.SELLER
        )

    def test_authenticated_user_can_get_own_profile(self):
        url = reverse('auth-me')

        self.client.force_authenticate(user=self.buyer)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.buyer.id)
        self.assertEqual(response.data['username'], 'buyer_me')
        self.assertEqual(response.data['email'], 'buyer_me@example.com')
        self.assertEqual(response.data['role'], UserProfile.Role.BUYER)

    def test_me_endpoint_return_correct_role_for_seller(self):
        url = reverse('auth-me')

        self.client.force_authenticate(user=self.seller)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'seller_me')
        self.assertEqual(response.data['role'], UserProfile.Role.SELLER)

    def test_anonymous_user_cannot_get_me_profile(self):
        url = reverse('auth-me')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
