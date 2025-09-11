from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (Product, Reviews, ProductImage,
                     Category, Wishlist, Reservation,
                     OrderItem, Order)
from PIL import Image

Users = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['user_id', 'username', 'email', 'phone', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Users.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['category_id', 'name', 'description']


class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    product_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def validate(self, data):
        product = data['product']
        quantity = data['quantity']
        if product.stock_quantity < quantity:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} units of '{product.name}' are available."
            )
        return data

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Error: Price cannot be 0')
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Error: Name cannot be blank')

    def validate_stock_quantity(self, value):
        if value < 0:
            raise serializers.ValidationError('stock cannot be nagative')
        return value

    def validate_product_images(self, value):
        img = Image.open(value)
        if img.format.lower() != 'jpeg':
            raise serializers.ValidationError('Only jpeg format is allowed')
        max_bytes_size = 5242880
        if value > max_bytes_size:
            raise serializers.ValidationError('Image size too Large')
        return value


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Reviews
        fields = ['reviews_id',
                  'product_id',
                  'user_id',
                  'comment',
                  'ratings',
                  'created_at']


class WishlistSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'user', 'product', 'product_name', 'added_at']
        read_only_fields = ['user', 'added_at']

    def validate_product(self, value):
        if not value.stock_quantity or value.stock_quantity <= 0:
            raise serializers.ValidationError("Product is out of stock.")
        return value


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ['reservation_id', 'user',
                  'product', 'quantity', 'reserved_at']
        read_only_fields = ['user', 'reserved_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')

    class Meta:
        model = OrderItem
        fields = ['product', 'product_name', 'price', 'quantity']

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def validate(self, data):
        product = data['product']
        if product.stock_quantity < data['quantity']:
            raise serializers.ValidationError(
                f"Only {product.stock_quantity} units of '{product.name}' are available."
            )
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = Order
        fields = ['order_id', 'user', 'tx_ref', 'total_amount', 'created_at', 'items']

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total amount must be greater than zero.")
        return value

    def validate_tx_ref(self, value):
        if Order.objects.filter(tx_ref=value).exists():
            raise serializers.ValidationError("Transaction reference already exists.")
        return value
