# product_api/views.py

from rest_framework import generics, viewsets, permissions, parsers, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied
from .models import (Product, ProductImage, Reviews,
                     Reservation, Wishlist, Category,
                     Order, OrderItem, Users)
from .serializer import (
    ProductSerializer, ProductImageSerializer, WishlistSerializer,
    ReservationSerializer, CategorySerializer, ReviewSerializer,
    OrderItemSerializer, OrderSerializer
)
from .filters import ProductFilter
from .pagination import (ProductPagination, ReviewsPagination,
                         CategoryPagination)
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import requests
from django.conf import settings


# Product Views
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    filterset_class = ProductFilter


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    pagination_class = ProductPagination


class ProductDetailsView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        product = self.get_object()
        if product.user != self.request.user:
            raise PermissionDenied('You are not authorized to update this product.')
        serializer.save()


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('You are not authorized to delete this product.')
        instance.delete()


class ProductImageUploadView(generics.CreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]


# Category Views
class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('category_id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['name', 'description']
    filterset_fields = ['name']
    pagination_class = CategoryPagination


# Review Views
class ReviewsCreateView(generics.CreateAPIView):
    queryset = Reviews.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewsListView(generics.ListAPIView):
    queryset = Reviews.objects.all().order_by('reviews_id')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ReviewsPagination


# Reservation Views
class ReserveProductView(generics.CreateAPIView):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderItemListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


class OrderItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)


class WishlistListCreateView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistDeleteView(generics.DestroyAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'wishlist_id'

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)


# wishlist Views
class WishlistCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        wishlist_items = Wishlist.objects.select_related('product').filter(user=user)

        if not wishlist_items.exists():
            return Response({'error': 'Your wishlist is empty.'}, status=400)

        total_amount = sum(item.product.price for item in wishlist_items)
        tx_ref = f"wishlist-{user.user_id}-{int(timezone.now().timestamp())}"

        payload = {
            "amount": str(total_amount),
            "currency": "ETB",
            "email": user.email,
            "first_name": user.first_name or "Customer",
            "last_name": user.last_name or "",
            "tx_ref": tx_ref,
            "callback_url": settings.CHAPA_WEBHOOK_URL,
            "return_url": settings.CHAPA_RETURN_URL,
            "customization": {
                "title": "Wishlist Checkout",
                "description": f"Payment for {wishlist_items.count()} wishlist item(s)"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(f"{settings.CHAPA_API_URL}/v1/transaction/initialize", json=payload, headers=headers)
            data = response.json()

            if data.get("status") != "success":
                return Response({'error': data.get("message", "Failed to initiate payment")}, status=500)

            checkout_url = data["data"]["checkout_url"]
            return Response({
                "checkout_url": checkout_url,
                "tx_ref": tx_ref,
                "amount": total_amount,
                "items": [item.product.name for item in wishlist_items]
            })

        except Exception as e:
            return Response({'error': f'Payment initiation failed: {str(e)}'}, status=500)


@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_payment(request):
    tx_ref = request.data.get('tx_ref')

    if not tx_ref:
        return Response({'error': 'Missing tx_ref'}, status=400)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(f"{settings.CHAPA_API_URL}/v1/transaction/verify/{tx_ref}", headers=headers)
        result = response.json()

        if result.get("status") != "success":
            return Response({'error': 'Payment not successful'}, status=400)

        email = result['data']['customer']['email']
        amount = result['data']['amount']
        user = Users.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'User not found'}, status=404)

        order = Order.objects.create(
            user=user,
            tx_ref=tx_ref,
            total_amount=amount,
            created_at=timezone.now()
        )

        wishlist_items = Wishlist.objects.select_related('product').filter(user=user)
        for item in wishlist_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=1
            )

        wishlist_items.delete()

        send_mail(
            subject='Order Confirmation',
            message=f'Thank you for your payment! Your order {order.order_id} has been confirmed.',
            from_email='noreply@yourdomain.com',
            recipient_list=[user.email],
            fail_silently=True
        )

        return Response({
            'message': 'Payment verified and order created successfully',
            'order_id': str(order.order_id),
            'tx_ref': tx_ref,
            'amount': amount
        })

    except Exception as e:
        return Response({'error': str(e)}, status=500)
