from django.core.management.base import BaseCommand
from product_api.models import BlockedIP
import ipaddress


class Command(BaseCommand):
    help = 'Unblock an IP address by removing it from the BlockedIP model'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='IP address to unblock')

    def handle(self, *args, **kwargs):
        ip = kwargs['ip_address']

        # Validate IP format
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid IP address: {ip}"))
            return

        deleted, _ = BlockedIP.objects.filter(ip_address=ip).delete()
        if deleted:
            self.stdout.write(self.style.SUCCESS(f"Unblocked IP: {ip}"))
        else:
            self.stdout.write(self.style.WARNING(f"IP {ip} was not found in blocklist."))
