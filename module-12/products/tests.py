from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


User = get_user_model()


class ProductAuthTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Books")
        self.product = Product.objects.create(
            name="Cookbook",
            price="25.00",
            stock=10,
            category=self.category,
        )

    def test_product_mutation_views_redirect_anonymous_users_to_login(self):
        protected_urls = [
            reverse("shop:add_product"),
            reverse("shop:edit_product", args=[self.product.pk]),
            reverse("shop:delete_product", args=[self.product.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_non_staff_user_cannot_manage_products(self):
        user = User.objects.create_user(
            username="shopper",
            password="S3curePassw0rd!2026",
        )
        self.client.force_login(user)

        protected_urls = [
            reverse("shop:add_product"),
            reverse("shop:edit_product", args=[self.product.pk]),
            reverse("shop:delete_product", args=[self.product.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("shop:product_list"))

        self.assertEqual(Product.objects.count(), 1)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_staff_user_can_open_product_management_pages(self):
        staff_user = User.objects.create_user(
            username="manager",
            password="S3curePassw0rd!2026",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        management_urls = [
            reverse("shop:add_product"),
            reverse("shop:edit_product", args=[self.product.pk]),
            reverse("shop:delete_product", args=[self.product.pk]),
        ]

        for url in management_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
