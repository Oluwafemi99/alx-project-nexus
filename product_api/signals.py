from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Reservation, Product, OrderItem, Order, Account
from .tasks import send_low_stock_email, send_order_confirmation_email
from django.core.cache import cache
from django.db import transaction


STOCK_THRESHOLD = 5


@receiver(pre_save, sender=Reservation)
def block_if_stock_low(sender, instance, **kwargs):
    product = instance.product
    if instance.quantity > product.stock_quantity:
        raise ValidationError(f"Insufficient stock for '{product.name}'. Only {product.stock_quantity} left.")


@receiver(post_save, sender=Reservation)
def notify_low_stock(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        if product.stock_quantity <= STOCK_THRESHOLD:
            send_low_stock_email.delay(product.name, product.stock_quantity, 'admin@yourdomain.com')


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_property_cache(sender, **kwargs):
    cache.delete('all_properties')


@receiver(post_save, sender=Order)
def handle_order_created(sender, instance, created, **kwargs):
    if created:
        # Send confirmation email asynchronously
        send_order_confirmation_email.delay(
            order_id=str(instance.order_id),
            user_email=instance.user.email
        )


"""" # handled atomically in views
@receiver(post_save, sender=OrderItem)
def reduce_stock_on_order_item_creation(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        if product.stock_quantity >= instance.quantity:
            print(f"Before reduction: {product.name} has {product.stock_quantity} quantity's")
            product.stock_quantity -= instance.quantity
            product.save()
            print(f"Stock reduced: {product.name} now {product.stock_quantity} quantity's")
        else:
            print(f"Not enough stock for {product.name} (requested {instance.quantity})")

"""
