from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status
from product_api.models import Users, Category, Product


# Test for User Registration, Login
@override_settings(RATELIMIT_ENABLE=False)  # Disable ratelimit in tests
class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {"username": "testuser", "password": "password123"}

    def test_user_registration(self):
        response = self.client.post("/api/register/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Users.objects.filter(username="testuser").exists())

    def test_user_login(self):
        Users.objects.create_user(**self.user_data)
        response = self.client.post("/api/token/", self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


# Test for Categories and Products
@override_settings(RATELIMIT_ENABLE=False)
class CategoryProductTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = Users.objects.create_user(
            username="tester", password="password123"
        )
        # Authenticate with JWT
        response = self.client.post("/api/token/", {
            "username": "tester",
            "password": "password123",
        }, format="json")

        if response.status_code != 200:
            raise Exception(f"JWT auth failed: {response.status_code} {response.content}")

        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        self.category_data = {
            "name": "Shoes",
            "description": "Footwear collection"
        }
        self.product_data = {
            "name": "Sneakers",
            "description": "Running sneakers",
            "price": "50.00",
            "stock_quantity": 10,
            "image_url": "http://example.com/sneakers.jpg",
        }

    def test_create_category(self):
        response = self.client.post("/api/categories/", self.category_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Category.objects.filter(name="Shoes").exists())

    def test_create_product(self):
        category = Category.objects.create(
            name="Clothes", description="Wearable stuff"
        )
        data = {
            "name": "Sneakers",
            "description": "Running sneakers",
            "price": "50.00",
            "stock_quantity": 10,
            "image_url": "http://example.com/sneakers.jpg",
            "category": str(category.category_id),  # send FK as UUID
        }
        response = self.client.post("/api/products/create/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(Product.objects.filter(name="Sneakers").exists())

    def test_list_products(self):
        category = Category.objects.create(name="Bags", description="Carry bags")
        Product.objects.create(
            name="Backpack",
            description="Laptop backpack",
            price="30.00",
            stock_quantity=5,
            image_url="http://example.com/backpack.jpg",
            category=category,
            user_id=self.user,
        )
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        self.assertGreaterEqual(len(response.data), 1)
