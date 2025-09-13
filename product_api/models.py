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
    image_url = models.URLField(blank=True)
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
        return f'{self.product_id}: {self.ratings}'


class ProductImage(models.Model):
    product_image_id = models.UUIDField(
        primary_key=True, editable=False, db_index=True, default=uuid.uuid4)
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='product_images/')


class Wishlist(models.Model):
    wishlist_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE,
        related_name='wishlist')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicates

    def __str__(self):
        return f"{self.user.username} → {self.product.name}"


class Reservation(models.Model):
    reservation_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE, related_name='reservations')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='reservations')
    quantity = models.PositiveIntegerField()
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reserved {self.quantity} of {self.product.name}"


class Transaction(models.Model):
    tx_ref = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class Account(models.Model):
    account_id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, db_index=True
    )
    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    total_stock_sold = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales: {self.total_sales_amount}, Transactions: {self.total_transactions}, Stock Sold: {self.total_stock_sold}"


class Order(models.Model):
    order_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='orders')
    tx_ref = models.CharField(max_length=100, unique=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}: {self.order_id}'


class OrderItem(models.Model):
    orderitem_id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                                    db_index=True, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.order


class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField()
    path = models.CharField(max_length=2048)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.ip_address} at {self.timestamp} -> {self.path}"


class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return self.ip_address


class SuspiciousIP(models.Model):
    ip_address = models.GenericIPAddressField()
    reason = models.TextField()

    def __str__(self):
        return f'{self.ip_address}, {self.reason}'


class DailySales(models.Model):
    daily_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(auto_now_add=True)
    total_sales_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_transactions = models.PositiveIntegerField(default=0)
    total_stock_sold = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"DailySales {self.date}"
