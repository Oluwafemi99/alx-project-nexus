# product_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCreateView, ProductListView, ProductSearchView, ProductDetailsView,
    ProductUpdateView, ProductDeleteView, ProductImageUploadView,
    CategoryView, ReviewsCreateView, ReviewsListView,
    WishlistListCreateView, WishlistDeleteView,
    WishlistCheckoutView, OrderListCreateView, OrderItemDetailView,
    OrderDetailView, OrderItemListCreateView, ReservationViewSet,
    ProductImageListView, verify_payment, GlobalAccountListView,
    DailySalesListView, BlockedIPListView, RequestLogListView,
    SuspiciousIPListView, ReservationCheckoutView, verify_Reserve_payment,
    RelatedProductViews)
from .auth import (CustomTokenObtainPairView, CustomTokenRefreshView,
                   LogoutView, RegisterView)

router = DefaultRouter()
router.register(r'categories', CategoryView, basename='category')
router.register(r'reservations', ReservationViewSet, basename='reservation')

urlpatterns = [
    # Product URLs
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductListView.as_view(), name='list-all-product'),
    path('products/search/', ProductSearchView.as_view(), name='search-product'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product-details'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/image/upload/', ProductImageUploadView.as_view(), name='product-image-upload'),
    path('Product/image/', ProductImageListView.as_view(), name='get-all-images'),

    # Reservation and Category URLs (via router)
    path('', include(router.urls)),

    # Review URLs
    path('reviews/create/', ReviewsCreateView.as_view(), name='review-create'),
    path('reviews/', ReviewsListView.as_view(), name='review-list'),

    # Reservation URLs
    path('reservation/checkout/', ReservationCheckoutView.as_view(), name='reservation-checkout'),
    path('verify/reserve_payment/', verify_Reserve_payment, name='verify-reserve-payment'),

    # Wishlist URLs
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist-list-create'),
    path('wishlist/<int:wishlist_id>/delete/', WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('wishlist/checkout/', WishlistCheckoutView.as_view(), name='wishlist-checkout'),
    path("chapa-webhook/", verify_payment, name="verify-payment"),

    # Order and OrderItems Urls
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),

    # Auth Urls
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Global Account View
    path('admin/global-accounts/', GlobalAccountListView.as_view(), name='global-account-list'),
    path('admin/daily-sales/', DailySalesListView.as_view(), name='daily-sales'),

    # Admin view for security checks
    path('admin/suspicious-ip/', SuspiciousIPListView.as_view(), name='suspicious-ip'),
    path('admin/blocked-ip/', BlockedIPListView.as_view(), name='blocked-ip'),
    path('admin/request-log/', RequestLogListView.as_view(), name='request-log'),

    # Related Product View
    path("products/<uuid:pk>/related/", RelatedProductViews.as_view(), name="related-products"),
]
