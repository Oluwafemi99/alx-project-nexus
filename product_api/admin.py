from django.contrib import admin
from .models import Users, Product, Category, Reviews, ProductImage, Order, OrderItem


@admin.register(Users)
class UsersAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'username', 'email', 'first_name', 'last_name']
    search_fields = ['username', 'email']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'description', 'price', 'category', 'stock_quantity', 'image_url', 'created_at', 'user_id']
    search_fields = ['name', 'description']
    list_filter = ['category', 'created_at']



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name', 'description']
    search_fields = ['name']


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    list_display = ['reviews_id', 'user_id', 'product_id', 'comment', 'ratings', 'created_at']
    list_filter = ['ratings', 'created_at']
    search_fields = ['comment']


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product_image_id', 'product_id', 'image']
    search_fields = ['product__name']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_id', 'user', 'tx_ref', 'total_amount', 'created_at']
    list_filter = ['created_at']
    search_fields = ['tx_ref', 'user__username']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'price', 'quantity']
    list_filter = ['product']
    search_fields = ['product__name']
