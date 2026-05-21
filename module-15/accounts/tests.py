from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Order, Product


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

    def test_dashboard_redirects_regular_users(self):
        user = User.objects.create_user(username="shopper", password="S3curePassw0rd!2026")
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertRedirects(response, reverse("shop:home"))

    def test_dashboard_link_is_hidden_for_regular_users(self):
        user = User.objects.create_user(username="shopper", password="S3curePassw0rd!2026")
        self.client.force_login(user)

        response = self.client.get(reverse("shop:home"))

        self.assertNotContains(response, "Dashboard")
        self.assertNotContains(response, "Orders")

    def test_dashboard_shows_staff_account_type(self):
        user = User.objects.create_user(
            username="manager",
            password="S3curePassw0rd!2026",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Staff account")

    def test_dashboard_link_is_visible_for_staff_users(self):
        user = User.objects.create_user(
            username="manager",
            password="S3curePassw0rd!2026",
            is_staff=True,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("shop:home"))

        self.assertContains(response, "Dashboard")

    def test_dashboard_shows_superuser_account_type(self):
        user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="S3curePassw0rd!2026",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:dashboard"))

        self.assertContains(response, "Superuser account")

    def test_my_account_shows_customer_order_history(self):
        user = User.objects.create_user(
            username="buyer",
            email="buyer@example.com",
            password="S3curePassw0rd!2026",
        )
        category = Category.objects.create(name="Books")
        product = Product.objects.create(
            name="Cookbook",
            price="25.00",
            stock=10,
            category=category,
        )
        order = Order.objects.create(
            user=user,
            full_name="Buyer Example",
            email="buyer@example.com",
            phone="08000000000",
            address="12 Market Street, Lagos",
            total_amount="25.00",
        )
        order.items.create(
            product=product,
            product_name=product.name,
            unit_price=product.price,
            quantity=1,
            line_total=product.price,
        )
        self.client.force_login(user)

        response = self.client.get(reverse("accounts:my_account"))

        self.assertContains(response, "My Account")
        self.assertContains(response, f"Order #{order.pk}")
        self.assertContains(response, "NGN 25.00")
