from django.utils.timezone import now
from django.http import HttpResponseForbidden
from django.core.cache import cache
from .models import RequestLog, BlockedIP
import ipinfo

access_token = '7567b26db7c484'
ipinfo_handler = ipinfo.getHandler(access_token)


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract IP address
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

        # Block if IP is in BlockedIP
        if BlockedIP.objects.filter(ip_address=ip_address).exists():
            return HttpResponseForbidden("Access denied.")

        # Geolocation: check cache first
        cache_key = f"geo:{ip_address}"
        geo_data = cache.get(cache_key)

        if not geo_data:
            try:
                details = ipinfo_handler.getDetails(ip_address)
                geo_data = {
                    'country': details.country_name or '',
                    'city': details.city or ''
                }
                # Cache for 24 hours
                cache.set(cache_key, geo_data, timeout=86400)
            except Exception:
                geo_data = {'country': '', 'city': ''}

        # Log the request
        RequestLog.objects.create(
            ip_address=ip_address,
            timestamp=now(),
            path=request.path,
            country=geo_data['country'],
            city=geo_data['city']
        )

        return self.get_response(request)
