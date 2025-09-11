from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Reservation, Product
from .tasks import send_low_stock_email


STOCK_THRESHOLD = 5


@receiver(post_save, sender=Reservation)
def reduce_stock_on_reservation(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        if product.stock_quantity < instance.quantity:
            raise ValidationError("Not enough stock available")
        product.stock_quantity -= instance.quantity
        product.save()


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


