import json

from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from .factories import UserFactory

User = get_user_model()


class TestUserViewSet(APITestCase):

    def setUp(self):
        self.unauthorized_client = APIClient()

        self.user = UserFactory.create()
        self.authorized_client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.authorized_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.api = '/api/v1/auth/users/'

        self.data = {
            "email": "user@test.com",
            "password": "someComplexPass123",
            "re_password": "someComplexPass123",
        }

        self.users_count = User.objects.count()

    def test_create_user(self):

        response = self.unauthorized_client.post(
            self.api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), self.users_count + 1)
        response = response.json()
        user = User.objects.last()
        self.assertTrue(user.is_active)
        self.assertEqual(response.get('id'), user.id)
        self.assertEqual(response.get('email'), self.data.get('email'))
        # check user data
        self.assertEqual(response.get('email'), user.email)

    def test_create_user_with_empty_data(self):
        data = {}
        response = self.unauthorized_client.post(
            self.api,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), self.users_count)
        response = response.json()
        self.assertEqual(len(response.keys()), 3)
        self.assertEqual(response.get('email'), ['This field is required.'])
        self.assertEqual(response.get('password'), ['This field is required.'])
        self.assertEqual(response.get('re_password'), ['This field is required.'])

    def test_create_user_wrong_password_validation(self):
        self.data['password'] = "pass"
        self.data['re_password'] = "pass"

        response = self.unauthorized_client.post(
            self.api,
            data=json.dumps(self.data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), self.users_count)
        response = response.json()
        self.assertEqual(response.get('password'),
                         ['This password is too short. It must contain at least 8 characters.',
                          'This password is too common.'])

    def test_create_user_with_invalid_confirm_password(self):
        self.data['re_password'] = "new_password"

        response = self.unauthorized_client.post(
            self.api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), self.users_count)
        response = response.json()
        self.assertEqual(response.get('non_field_errors'), ["The two password fields didn't match."])

    def test_create_user_with_duplicate_email(self):
        UserFactory(email='test@test.com')
        self.assertEqual(User.objects.count(), 2)

        self.data['email'] = 'test@test.com'

        response = self.unauthorized_client.post(
            self.api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(User.objects.count(), 2)
        response = response.json()
        self.assertEqual(response.get('email'), ['user with this email address already exists.'])

    def test_get_user_profile_info(self):
        response = self.authorized_client.get(
            '{}{}/'.format(self.api, 'me'),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response.keys()), 2)
        self.assertEqual(response.get('id'), self.user.id)
        self.assertEqual(response.get('email'), self.user.email)


class TestUserAuthentications(APITestCase):

    def setUp(self):
        self.user = UserFactory.create()
        self.client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.login_api = '/api/v1/auth/token/login/'
        self.logout_api = '/api/v1/auth/token/logout/'

    def test_login_with_user(self):
        self.user.set_password("NewPassword")
        self.user.save()

        data = {
            "email": self.user.email,
            "password": "NewPassword"
        }
        response = self.client.post(
            self.login_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIsNotNone(response.get('auth_token'))

    def test_login_with_empty_data(self):
        self.user.set_password("NewPassword")
        self.user.save()

        data = {}
        response = self.client.post(
            self.login_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response.get('non_field_errors'), ['Unable to log in with provided credentials.'])

    def test_login_with_invalid_credentials(self):
        data = {
            "email": self.user.email,
            "password": "NewPassword"
        }
        response = self.client.post(
            self.login_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response.get('non_field_errors'), ['Unable to log in with provided credentials.'])

    def test_logout(self):
        data = {}
        self.assertEqual(Token.objects.filter(user=self.user).count(), 1)
        response = self.client.post(
            self.logout_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Token.objects.filter(user=self.user).count(), 0)
