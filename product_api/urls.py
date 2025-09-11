# product_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductCreateView, ProductListView, ProductSearchView, ProductDetailsView,
    ProductUpdateView, ProductDeleteView, ProductImageUploadView,
    CategoryView, ReviewsCreateView, ReviewsListView,
    ReserveProductView, WishlistListCreateView, WishlistDeleteView,
    WishlistCheckoutView, OrderListCreateView, OrderItemDetailView,
    OrderDetailView, OrderItemListCreateView
)

router = DefaultRouter()
router.register(r'categories', CategoryView, basename='category')

urlpatterns = [
    # Product URLs
    path('products/create/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/search/', ProductSearchView.as_view(), name='product-search'),
    path('products/<int:pk>/', ProductDetailsView.as_view(), name='product-detail'),
    path('products/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('products/<int:pk>/delete/', ProductDeleteView.as_view(), name='product-delete'),
    path('products/image/upload/', ProductImageUploadView.as_view(), name='product-image-upload'),

    # Category URLs (via router)
    path('', include(router.urls)),

    # Review URLs
    path('reviews/create/', ReviewsCreateView.as_view(), name='review-create'),
    path('reviews/', ReviewsListView.as_view(), name='review-list'),

    # Reservation URLs
    path('reservations/create/', ReserveProductView.as_view(), name='reservation-create'),

    # Wishlist URLs
    path('wishlist/', WishlistListCreateView.as_view(), name='wishlist-list-create'),
    path('wishlist/<int:wishlist_id>/delete/', WishlistDeleteView.as_view(), name='wishlist-delete'),
    path('wishlist/checkout/', WishlistCheckoutView.as_view(), name='wishlist-checkout'),

    # Order and OrderItems Urls
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<uuid:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('order-items/', OrderItemListCreateView.as_view(), name='orderitem-list-create'),
    path('order-items/<int:pk>/', OrderItemDetailView.as_view(), name='orderitem-detail'),
]
