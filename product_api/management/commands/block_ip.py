from django.core.management.base import BaseCommand
from product_api.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Block an IP address by adding it to the BlockedIP model'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to block')

    def handle(self, *args, **kwargs):
        ip = kwargs['ip_address']

        # Validate IP format
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid IP address: {ip}"))
            return

        # Add to BlockedIP model
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Blocked IP: {ip}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP {ip} is already blocked."))
