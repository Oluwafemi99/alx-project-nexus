from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Product, Reviews, ProductImage, Category
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
