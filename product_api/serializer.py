from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import (Product, Reviews, ProductImage,
                     Category, Wishlist, Reservation,
                     OrderItem, Order, Account, DailySales,
                     RequestLog, BlockedIP, SuspiciousIP,
                     Transaction)
from PIL import Image
from rest_framework_simplejwt.serializers import (TokenObtainPairSerializer,
                                                  TokenRefreshSerializer)

Users = get_user_model()

""""
Serializer for Models
"""


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['user_id'] = str(user.user_id)  # include UUID in token payload
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = attrs.get("refresh")

        try:
            token = RefreshToken(refresh)
        except TokenError as e:
            raise InvalidToken(
                {"detail": "Invalid refresh token", "error": str(e)})

        # Create new access token
        access_token = str(token.access_token)
        return {
            "access": access_token,
            "refresh": str(token),
        }


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Users
        fields = ['user_id', 'username', 'email', 'phone',
                  'password', 'first_name', 'last_name']

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


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(source='user_id')  # or include username/email

    class Meta:
        model = Reviews
        fields = ['reviews_id', 'user', 'comment', 'ratings', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    # Accept UUID instead of full object
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    reviews = ReviewSerializer(many=True, read_only=True)
    avg_rating = serializers.FloatField(read_only=True)
    # User will be set automatically in perform_create
    user_id = serializers.UUIDField(read_only=True)
    product_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = [
            "product_id",
            "name",
            "description",
            "price",
            "stock_quantity",
            "image_url",
            "category",
            "user_id",
            "product_images",
            "reviews",
            "avg_rating",
        ]
        read_only_fields = ("product_id", "created_at", "user_id")

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Error: Price cannot be 0')
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError('Error: Name cannot be blank')
        return value

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


class WishlistSerializer(serializers.ModelSerializer):
    product = serializers.StringRelatedField()
    user = serializers.StringRelatedField()
    product_images = ProductImageSerializer(many=True, read_only=True)

    class Meta:
        model = Wishlist
        fields = ['wishlist_id', 'user', 'product',
                  'added_at', 'quantity', 'product_images']
        read_only_fields = ['user', 'added_at']

    def validate_product(self, value):
        if not value.stock_quantity or value.stock_quantity <= 0:
            raise serializers.ValidationError("Product is out of stock.")
        return value

    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity", 1)

        if quantity > product.stock_quantity:
            raise serializers.ValidationError(
                {"quantity": f"Only {product.stock_quantity} units available for {product.name}"}
            )
        return data


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
        fields = ['order_id', 'user', 'tx_ref',
                  'total_amount', 'created_at', 'items']

    def validate_total_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Total amount must be greater than zero.")
        return value

    def validate_tx_ref(self, value):
        if Order.objects.filter(tx_ref=value).exists():
            raise serializers.ValidationError(
                "Transaction reference already exists.")
        return value


class AccountSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ['account_id', 'total_sales_amount',
                  'total_transactions', 'total_stock_sold', 'updated_at']


class DailySalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailySales
        fields = '__all__'


class RequestlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = RequestLog
        fields = '__all__'


class BlockedIPSerializer(serializers.ModelSerializer):

    class Meta:
        model = BlockedIP
        fields = '__all__'


class SupiciousIPSerializer(serializers.ModelSerializer):

    class Meta:
        model = SuspiciousIP
        fields = "__all__"


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['tx_ref', 'user', 'amount', 'created_at', 'status']
        read_only_fields = ['status']
