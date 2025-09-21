# product_api/views.py

from rest_framework import generics, viewsets, permissions, parsers, filters
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import PermissionDenied
from .models import (Product, ProductImage, Reviews,
                     Reservation, Wishlist, Category,
                     Order, OrderItem, Users, Account,
                     DailySales, BlockedIP, RequestLog, SuspiciousIP)
from .serializer import (
    ProductSerializer, ProductImageSerializer, WishlistSerializer,
    ReservationSerializer, CategorySerializer, ReviewSerializer,
    OrderItemSerializer, OrderSerializer, AccountSerializer,
    DailySalesSerializer, SupiciousIPSerializer, BlockedIPSerializer,
    RequestlogSerializer)
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
from .utils import get_all_products
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
import logging
from decimal import Decimal
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

logger = logging.getLogger(__name__)


# Product Create Views
class ProductCreateView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)


# product List View
@method_decorator(csrf_exempt, name='dispatch')
@method_decorator(cache_page(60 * 15), name='dispatch')
class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    permission_classes = [permissions.AllowAny]
    filterset_class = ProductFilter

    def get_queryset(self):
        return get_all_products()


class ProductSearchView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter,
                       filters.OrderingFilter]
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at']
    pagination_class = ProductPagination


class ProductDetailsView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_update(self, serializer):
        product = self.get_object()
        if product.user_id != self.request.user:
            raise PermissionDenied('You are not authorized to update this product.')
        serializer.save()


class ProductDeleteView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('You are not authorized to delete this product.')
        instance.delete()


class ProductImageUploadView(generics.CreateAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]


class ProductImageListView(generics.ListAPIView):
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.AllowAny]


# Category Views
class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by('category_id')
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
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
        serializer.save(user_id=self.request.user)


class ReviewsListView(generics.ListAPIView):
    queryset = Reviews.objects.all().order_by('reviews_id')
    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ReviewsPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['product']  # Enables ?product=UUID filtering


# Order Views
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


# wishlist Views
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


# Reservation Views
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Only show reservations for the logged-in user
        return self.queryset.filter(user=self.request.user)


#  Checkout Views
class WishlistCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        wishlist_items = Wishlist.objects.select_related(
            'product').filter(user=user)
        if not wishlist_items.exists():
            return Response({'error': 'Your wishlist is empty.'}, status=400)

        for item in wishlist_items:
            if item.quantity > item.product.stock_quantity:
                return Response({
                    'error': f"Product '{item.product.name}' only has {item.product.stock_quantity} items available"
                }, status=400)

        total_amount = sum(
            item.product.price * item.quantity for item in wishlist_items)
        tx_ref = f"wl-{str(user.user_id)[:8]}-{int(timezone.now().timestamp())}"

        payload = {
            "amount": str(total_amount),
            "currency": "ETB",
            "email": user.email or "tobi@example.com",
            "first_name": user.first_name or "Customer",
            "last_name": user.last_name or "",
            "tx_ref": tx_ref,
            "callback_url": "https://0911b83c8cae.ngrok-free.app/chapa-webhook/",
            "return_url": settings.CHAPA_RETURN_URL,
            "customization": {
                "title": "WishlistPay",
                "description": f"Payment for {wishlist_items.count()} wishlist items"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET}",
            "Content-Type": "application/json"
        }
        logger.info("Chapa payload: %s", payload)
        try:
            response = requests.post(
                f"{settings.CHAPA_API_URL}/v1/transaction/initialize", json=payload, headers=headers)
            data = response.json()

            if data.get("status") != "success":
                return Response(
                    {'error': data.get("message", "Failed to initiate payment")}, status=500)

            checkout_url = data["data"]["checkout_url"]
            return Response({
                "checkout_url": checkout_url,
                "tx_ref": tx_ref,
                "amount": total_amount,
                "items": [
                    {"product": item.product.name, "quantity": item.
                     quantity, "subtotal": item.product.price * item.quantity}
                    for item in wishlist_items
                ]
            })

        except Exception as e:
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'}, status=500)


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
        # Verify payment with Chapa
        response = requests.get(
            f"{settings.CHAPA_API_URL}/v1/transaction/verify/{tx_ref}",
            headers=headers)

        result = response.json()

        if result.get("status") != "success" or "data" not in result:
            return Response({'error': 'Payment not successful'}, status=400)

        data = result["data"]
        email = data.get("customer", {}).get("email")
        amount = Decimal(data.get("amount", "0"))

        # Get user from tx_ref OR email
        short_uuid = tx_ref.split("-")[1]
        user = Users.objects.filter(user_id__startswith=short_uuid).first() \
            or Users.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'User not found'}, status=404)

        wishlist_items = Wishlist.objects.select_related(
            'product').filter(user=user)
        if not wishlist_items.exists():
            return Response({'error': 'Your wishlist is empty.'}, status=400)

        with transaction.atomic():
            # Check stock and reduce it atomically
            for item in wishlist_items:
                product = Product.objects.select_for_update().get(
                    product_id=item.product.product_id)
                if item.quantity > product.stock_quantity:
                    return Response({
                        'error': f"Product '{product.name}' only has {product.stock_quantity} items available"
                    }, status=400)
                print(f"Before reduction: {product.name} has {product.stock_quantity} quantity's")
                product.stock_quantity -= item.quantity
                product.save()
                print(f"Stock reduced: {product.name} now {product.stock_quantity} quantity's")

            # Create the order
            order = Order.objects.create(
                user=user,
                tx_ref=tx_ref,
                total_amount=amount,
                created_at=timezone.now()
            )

            # Create order items
            for item in wishlist_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # Update global account
            stock_sold = sum(item.quantity for item in wishlist_items)
            account, _ = Account.objects.get_or_create(
                account_id="00000000-0000-0000-0000-000000000001"
            )
            account.total_sales_amount += amount
            account.total_transactions += 1
            account.total_stock_sold += stock_sold
            account.save()
            print(f'{amount} has been added to Account')

            # Clear wishlist
            wishlist_items.delete()

        # Send confirmation email
        send_mail(
            subject='Order Confirmation',
            message=f'Thank you for your payment! Your order {order.order_id} has been confirmed.',
            from_email='noreply@yourdomain.com',
            recipient_list=[user.email],
            fail_silently=True
        )

        logger.info(
            f"User {user.email} verified payment {tx_ref}, order {order.order_id} created successfully.")

        return Response({
            'message': 'Payment verified and order created successfully',
            'order_id': str(order.order_id),
            'tx_ref': tx_ref,
            'amount': str(amount)
        })

    except Exception as e:
        logger.error(f"Payment verification failed for tx_ref {tx_ref}: {str(e)}")
        return Response({'error': str(e)}, status=500)


class GlobalAccountListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = AccountSerializer
    queryset = Account.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'updated_at': ['gte', 'lte'],
    }


class DailySalesListView(generics.ListAPIView):
    queryset = DailySales.objects.all()
    serializer_class = DailySalesSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['date']


class BlockedIPListView(generics.ListAPIView):
    queryset = BlockedIP.objects.all()
    serializer_class = BlockedIPSerializer
    permission_classes = [permissions.IsAdminUser]


class RequestLogListView(generics.ListAPIView):
    queryset = RequestLog.objects.all()
    serializer_class = RequestlogSerializer
    permission_classes = [permissions.IsAdminUser]


# SuspiciousIPList View
class SuspiciousIPListView(generics.ListAPIView):
    queryset = SuspiciousIP.objects.all()
    serializer_class = SupiciousIPSerializer
    permission_classes = [permissions.IsAdminUser]


# Reserve Payment Checkout View
class ReservationCheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        reservation_items = Reservation.objects.select_related(
            'product').filter(user=user)
        if not reservation_items.exists():
            return Response({'error': 'Your wishlist is empty.'}, status=400)

        for item in reservation_items:
            if item.quantity > item.product.stock_quantity:
                return Response({
                    'error': f"Product '{item.product.name}' only has {item.product.stock_quantity} items available"
                }, status=400)

        total_amount = sum(
            item.product.price * item.quantity for item in reservation_items)
        tx_ref = f"Rl-{str(user.user_id)[:9]}-{int(timezone.now().timestamp())}"

        payload = {
            "amount": str(total_amount),
            "currency": "ETB",
            "email": user.email or "tobi@example.com",
            "first_name": user.first_name or "Customer",
            "last_name": user.last_name or "",
            "tx_ref": tx_ref,
            "callback_url": "https://0911b83c8cae.ngrok-free.app/chapa-webhook/",
            "return_url": settings.CHAPA_RETURN_URL,
            "customization": {
                "title": "WishlistPay",
                "description": f"Payment for {reservation_items.count()} Reserved items"
            }
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET}",
            "Content-Type": "application/json"
        }
        logger.info("Chapa payload: %s", payload)
        try:
            response = requests.post(
                f"{settings.CHAPA_API_URL}/v1/transaction/initialize", json=payload, headers=headers)
            data = response.json()

            if data.get("status") != "success":
                return Response({'error': data.get(
                    "message", "Failed to initiate payment")}, status=500)

            checkout_url = data["data"]["checkout_url"]
            return Response({
                "checkout_url": checkout_url,
                "tx_ref": tx_ref,
                "amount": total_amount,
                "items": [
                    {"product": item.product.name, "quantity": item.
                     quantity, "subtotal": item.product.price * item.quantity}
                    for item in reservation_items
                ]
            })

        except Exception as e:
            return Response(
                {'error': f'Payment initiation failed: {str(e)}'}, status=500)


# Verify Reserve payment view
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_Reserve_payment(request):
    tx_ref = request.data.get('tx_ref')

    if not tx_ref:
        return Response({'error': 'Missing tx_ref'}, status=400)

    headers = {
        "Authorization": f"Bearer {settings.CHAPA_SECRET}",
        "Content-Type": "application/json"
    }

    try:
        # Verify payment with Chapa
        response = requests.get(
            f"{settings.CHAPA_API_URL}/v1/transaction/verify/{tx_ref}",
            headers=headers
        )
        result = response.json()

        if result.get("status") != "success" or "data" not in result:
            return Response({'error': 'Payment not successful'}, status=400)

        data = result["data"]
        email = data.get("customer", {}).get("email")
        amount = Decimal(data.get("amount", "0"))

        # Get user from tx_ref OR email
        short_uuid = tx_ref.split("-")[1]
        user = Users.objects.filter(user_id__startswith=short_uuid).first() \
            or Users.objects.filter(email=email).first()

        if not user:
            return Response({'error': 'User not found'}, status=404)

        reserve_items = Reservation.objects.select_related(
            'product').filter(user=user)
        if not reserve_items.exists():
            return Response(
                {'error': 'Your Reserve list is empty.'}, status=400)

        with transaction.atomic():
            # Check stock and reduce it atomically
            for item in reserve_items:
                product = Product.objects.select_for_update().get(
                    product_id=item.product.product_id)
                if item.quantity > product.stock_quantity:
                    return Response({
                        'error': f"Product '{product.name}' only has {product.stock_quantity} items available"
                    }, status=400)
                print(f"Before reduction: {product.name} has {product.stock_quantity} quantity's")
                product.stock_quantity -= item.quantity
                product.save()
                print(f"Stock reduced: {product.name} now {product.stock_quantity} quantity's")

            # Create the order
            order = Order.objects.create(
                user=user,
                tx_ref=tx_ref,
                total_amount=amount,
                created_at=timezone.now()
            )

            # Create order items
            for item in reserve_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    price=item.product.price,
                    quantity=item.quantity
                )

            # Update global account
            stock_sold = sum(item.quantity for item in reserve_items)
            account, _ = Account.objects.get_or_create(
                account_id="00000000-0000-0000-0000-000000000001"
            )
            account.total_sales_amount += amount
            account.total_transactions += 1
            account.total_stock_sold += stock_sold
            account.save()
            print(f'{amount} has been added to Account')

            # Clear reservelist
            reserve_items.delete()

        # Send confirmation email
        send_mail(
            subject='Order Confirmation',
            message=f'Thank you for your payment! Your order {order.order_id} has been confirmed.',
            from_email='noreply@yourdomain.com',
            recipient_list=[user.email],
            fail_silently=True
        )

        logger.info(
            f"User {user.email} verified payment {tx_ref}, order {order.order_id} created successfully.")

        return Response({
            'message': 'Payment verified and order created successfully',
            'order_id': str(order.order_id),
            'tx_ref': tx_ref,
            'amount': str(amount)
        })

    except Exception as e:
        logger.error(
            f"Payment verification failed for tx_ref {tx_ref}: {str(e)}")
        return Response({'error': str(e)}, status=500)


class RelatedProductViews(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ProductSerializer

    def get(self, request, pk):
        # fetch the current product
        product = get_object_or_404(Product, pk=pk)

        # Get related products from the same category (excluding self)
        related_product = Product.objects.filter(
            category=product.category).exclude(pk=product.pk)[:6]

        if not related_product.exists():
            return Response(
                {
                    "message": "No related products found in this category.",
                    "results": []
                },
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(related_product, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
