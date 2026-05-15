from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class AuthViewTests(TestCase):
    def test_register_creates_and_logs_in_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "name": "Ada Lovelace",
                "email": "ada@example.com",
                "password": "S3curePassw0rd!2026",
                "confirm_password": "S3curePassw0rd!2026",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("shop:home"))
        user = User.objects.get(email="ada@example.com")
        self.assertEqual(user.username, "ada-lovelace")
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_login_accepts_email_address(self):
        user = User.objects.create_user(
            username="torilo",
            email="torilo@example.com",
            password="S3curePassw0rd!2026",
        )

        response = self.client.post(
            reverse("accounts:login"),
            {
                "username": "torilo@example.com",
                "password": "S3curePassw0rd!2026",
            },
            follow=True,
        )

        self.assertRedirects(response, reverse("shop:home"))
        self.assertEqual(self.client.session["_auth_user_id"], str(user.pk))

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("accounts:dashboard"))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_dashboard_shows_regular_account_type(self):
        user = User.objects.create_user(username="shopper", password="S3curePassw0rd!2026")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Regular customer account")

    def test_dashboard_shows_staff_account_type(self):
        user = User.objects.create_user(
            username="manager",
            password="S3curePassw0rd!2026",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Staff account")

    def test_dashboard_shows_superuser_account_type(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="S3curePassw0rd!2026",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Superuser account")
