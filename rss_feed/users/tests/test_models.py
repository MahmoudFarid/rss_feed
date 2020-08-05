from django.contrib.auth import get_user_model
from django.test import TestCase

from .factories import UserFactory

User = get_user_model()


class TestUserModel(TestCase):

    def test_create_user_model(self):
        self.assertEqual(User.objects.count(), 0)
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertEqual(User.objects.count(), 1)
