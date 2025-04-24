from django.test import TestCase, Client
from django.urls import reverse
from .models import User


class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="test", email="test@gmail.com", password="1234")

    def test_email(self):

        self.assertEqual(self.user.email, "test@gmail.com")

class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.registration_url = reverse('registration')
        self.login_url = reverse('login')
        self.logout_url = reverse("logout")

        self.user = User.objects.create_user(username="test", email="test@gmail.com", password="1234")
        self.client.login(email="test@gmail.com", password="1234")

    def test_registration_POST_logged_in(self):
        data = {"email": "test2@gmail.com", "username": "test2", "password1": "1234", "password2": "1234"}
        response = self.client.post(self.registration_url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_login_POST_logged_in(self):
        data = {"email": "test@gmail.com", "password": "1234"}
        response = self.client.post(self.login_url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_registration_POST_not_logged_in(self):
        self.client.logout()
        data = {"email": "test2@gmail.com", "username": "test2", "password1": "1234", "password2": "1234"}
        response = self.client.post(self.registration_url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_login_POST_not_logged_in(self):
        self.client.logout()
        data = {"email": "test@gmail.com", "password": "1234"}
        response = self.client.post(self.login_url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_logout_GET(self):
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)

    def test_login_POST_no_data(self):
        self.client.logout()
        response = self.client.post(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_registration_POST_no_data(self):
        self.client.logout()
        response = self.client.post(self.registration_url)
        self.assertEqual(response.status_code, 200)
    