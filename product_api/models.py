from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


# Create your models here.
class Users(AbstractUser):
    user_id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, db_index=True)
    phone = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return self.username


class Category(models.Model):
    category_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Product(models.Model):
    product_id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, db_index=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name='products')
    stock_quantity = models.IntegerField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='products')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Products'

    def __str__(self):
        return self.name


class Reviews(models.Model):
    reviews_id = models.UUIDField(
        primary_key=True, editable=False, default=uuid.uuid4, db_index=True)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reviews')
    user_id = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='reviews')
    comment = models.CharField(max_length=200)
    ratings = models.IntegerField(choices=[(i, i)for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product_id}: {self.Ratings}'


class ProductImage(models.Model):
    productimage_id = models.UUIDField(
        primary_key=True, editable=False, db_index=True, default=uuid.uuid4)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')
