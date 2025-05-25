from django.test import TestCase
from django.contrib.auth.models import User

class UserAuthTest(TestCase):
    def test_user_registration(self):
        response = self.client.post('/sign_up/', {
            'username': 'testuser',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='testuser').exists())
