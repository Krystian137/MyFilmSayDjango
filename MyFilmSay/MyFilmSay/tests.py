from django.test import TestCase
from django.urls import reverse
from .models import User, RoleEnum

class UserModelTest(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            password="password123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("password123"))
        self.assertEqual(user.role, RoleEnum.USER)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_superuser_creation(self):
        superuser = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("adminpassword"))
        self.assertEqual(superuser.role, RoleEnum.ADMIN)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_is_admin_property(self):
        user = User(role=RoleEnum.USER)
        self.assertFalse(user.is_admin)
        admin = User(role=RoleEnum.ADMIN)
        self.assertTrue(admin.is_admin)

    def test_is_moderator_property(self):
        user = User(role=RoleEnum.USER)
        self.assertFalse(user.is_moderator)
        moderator = User(role=RoleEnum.MODERATOR)
        self.assertTrue(moderator.is_moderator)

    def test_is_user_property(self):
        moderator = User(role=RoleEnum.MODERATOR)
        self.assertFalse(moderator.is_user)
        user = User(role=RoleEnum.USER)
        self.assertTrue(user.is_user)

class AuthTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            name="Test User",
            password="password123"
        )

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'name': 'New User',
            'email': 'new@example.com',
            'password': 'newpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_registration_with_existing_email(self):
        response = self.client.post(reverse('register'), {
            'name': 'Another User',
            'email': 'test@example.com',
            'password': 'password456'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_user_login_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
