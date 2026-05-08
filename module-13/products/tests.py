import json

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


class ProductAPITests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name="Books",
            description="Printed and digital books",
        )
        self.product = Product.objects.create(
            name="Cookbook",
            price="25.00",
            stock=10,
            category=self.category,
        )

    def test_product_list_returns_products_with_nested_category(self):
        response = self.client.get(reverse("shop:api_product_list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Cookbook")
        self.assertEqual(data[0]["category"]["name"], "Books")
        self.assertEqual(data[0]["category"]["product_count"], 1)

    def test_product_can_be_created_with_category_id(self):
        payload = {
            "name": "Novel",
            "price": "18.50",
            "stock": 7,
            "is_available": True,
            "category_id": self.category.pk,
        }

        response = self.client.post(
            reverse("shop:api_product_list"),
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.json()["category"]["name"], "Books")

    def test_product_detail_can_be_retrieved_updated_and_deleted(self):
        detail_url = reverse("shop:api_product_detail", args=[self.product.pk])

        retrieve_response = self.client.get(detail_url)
        self.assertEqual(retrieve_response.status_code, 200)
        self.assertEqual(retrieve_response.json()["name"], "Cookbook")

        update_payload = {
            "name": "Updated Cookbook",
            "price": "30.00",
            "stock": 5,
            "is_available": False,
            "category_id": self.category.pk,
        }
        update_response = self.client.put(
            detail_url,
            data=json.dumps(update_payload),
            content_type="application/json",
        )

        self.assertEqual(update_response.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Cookbook")
        self.assertEqual(self.product.stock, 5)
        self.assertFalse(self.product.is_available)

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_category_list_returns_categories_with_products(self):
        response = self.client.get(reverse("shop:api_category_list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Books")
        self.assertEqual(data[0]["product_count"], 1)
        self.assertEqual(data[0]["products"][0]["name"], "Cookbook")
        self.assertEqual(data[0]["products"][0]["category"]["name"], "Books")
