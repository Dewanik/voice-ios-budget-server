from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserSubscription, UserProfile


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_profile_creation(self):
        profile = UserProfile.objects.create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertIsNone(profile.phone_number)

    def test_user_subscription_creation(self):
        subscription = UserSubscription.objects.create(
            user=self.user,
            stripe_customer_id='cus_test123',
            status='active'
        )
        self.assertEqual(subscription.user, self.user)
        self.assertEqual(subscription.status, 'active')
