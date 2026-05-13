import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from .models import Category, Product


User = get_user_model()


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
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
        self.product.created_by = staff_user
        self.product.save()
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

    def test_category_mutation_views_redirect_anonymous_users_to_login(self):
        protected_urls = [
            reverse("shop:add_category"),
            reverse("shop:edit_category", args=[self.category.pk]),
            reverse("shop:delete_category", args=[self.category.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertTrue(response["Location"].startswith(reverse("accounts:login")))

    def test_non_staff_user_cannot_manage_categories(self):
        user = User.objects.create_user(
            username="category-shopper",
            password="S3curePassw0rd!2026",
        )
        self.client.force_login(user)

        protected_urls = [
            reverse("shop:add_category"),
            reverse("shop:edit_category", args=[self.category.pk]),
            reverse("shop:delete_category", args=[self.category.pk]),
        ]

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(response, reverse("shop:category_list"))

    def test_staff_user_can_open_category_management_pages(self):
        staff_user = User.objects.create_user(
            username="category-manager",
            password="S3curePassw0rd!2026",
            is_staff=True,
        )
        self.client.force_login(staff_user)

        management_urls = [
            reverse("shop:add_category"),
            reverse("shop:edit_category", args=[self.category.pk]),
            reverse("shop:delete_category", args=[self.category.pk]),
        ]

        for url in management_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)


@override_settings(PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"])
class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.password = "S3curePassw0rd!2026"
        self.user = User.objects.create_user(
            username="api-owner",
            password=self.password,
        )
        self.other_user = User.objects.create_user(
            username="another-owner",
            password=self.password,
        )
        self.category = Category.objects.create(
            name="Books",
            description="Printed and digital books",
        )
        self.electronics = Category.objects.create(
            name="Electronics",
            description="Useful devices",
        )
        self.product = Product.objects.create(
            name="Cookbook",
            price="25.00",
            stock=10,
            category=self.category,
            created_by=self.user,
        )

    def authenticate_as_owner(self):
        response = self.client.post(
            reverse("api_auth_token"),
            {"username": self.user.username, "password": self.password},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")

    def test_simple_auth_token_endpoint_returns_only_token(self):
        response = self.client.post(
            reverse("api_auth_token"),
            {"username": self.user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

    def test_jwt_token_endpoints_return_access_and_refresh_tokens(self):
        token_response = self.client.post(
            reverse("token_obtain_pair"),
            {"username": self.user.username, "password": self.password},
            format="json",
        )

        self.assertEqual(token_response.status_code, 200)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

        refresh_response = self.client.post(
            reverse("token_refresh"),
            {"refresh": token_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn("access", refresh_response.data)

    def test_product_list_returns_products_with_nested_category(self):
        response = self.client.get(reverse("shop:api_product_list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["count"], 1)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["name"], "Cookbook")
        self.assertEqual(data["results"][0]["created_by"], "api-owner")
        self.assertEqual(data["results"][0]["category"]["name"], "Books")
        self.assertEqual(data["results"][0]["category"]["product_count"], 1)

    def test_product_can_be_created_with_category_id(self):
        self.authenticate_as_owner()
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
        self.assertEqual(response.json()["created_by"], "api-owner")

    def test_product_detail_can_be_retrieved_updated_and_deleted(self):
        self.authenticate_as_owner()
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

    def test_product_writes_require_authentication_and_creator_ownership(self):
        detail_url = reverse("shop:api_product_detail", args=[self.product.pk])

        anonymous_response = self.client.delete(detail_url)
        self.assertEqual(anonymous_response.status_code, 401)

        token_response = self.client.post(
            reverse("api_auth_token"),
            {"username": self.other_user.username, "password": self.password},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token_response.data['token']}")

        forbidden_response = self.client.delete(detail_url)
        self.assertEqual(forbidden_response.status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_product_list_supports_pagination_filter_search_and_price_ordering(self):
        Product.objects.bulk_create(
            [
                Product(
                    name=f"Book {index}",
                    price=f"{10 + index}.00",
                    stock=5,
                    category=self.category,
                    created_by=self.user,
                )
                for index in range(1, 7)
            ]
            + [
                Product(
                    name="Laptop",
                    price="900.00",
                    stock=3,
                    category=self.electronics,
                    is_available=False,
                    created_by=self.user,
                )
            ]
        )

        paginated_response = self.client.get(reverse("shop:api_product_list"))
        self.assertEqual(paginated_response.status_code, 200)
        self.assertEqual(len(paginated_response.json()["results"]), 6)
        self.assertIsNotNone(paginated_response.json()["next"])

        filtered_response = self.client.get(
            reverse("shop:api_product_list"),
            {"category": self.electronics.pk, "is_available": "false", "search": "laptop"},
        )
        self.assertEqual(filtered_response.json()["count"], 1)
        self.assertEqual(filtered_response.json()["results"][0]["name"], "Laptop")

        ordered_response = self.client.get(
            reverse("shop:api_product_list"),
            {"ordering": "-price"},
        )
        self.assertEqual(ordered_response.json()["results"][0]["name"], "Laptop")

    def test_category_list_returns_categories_with_products(self):
        response = self.client.get(reverse("shop:api_category_list"))

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        books_data = next(category for category in data if category["name"] == "Books")
        self.assertEqual(books_data["product_count"], 1)
        self.assertEqual(books_data["products"][0]["name"], "Cookbook")
        self.assertEqual(books_data["products"][0]["category"]["name"], "Books")
