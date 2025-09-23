from .models import Product
from django.core.cache import cache
import logging
from django_redis import get_redis_connection
from django.db.models import Avg


# Caching All products View at Low level
def get_all_products():
    products = cache.get('all_products')
    if products is None:
        products = Product.objects.prefetch_related(
            'reviews__user_id').annotate(avg_rating=Avg('reviews__ratings'))
        cache.set('all_products', products, timeout=3600)
    return products


logger = logging.getLogger(__name__)


# Logging Redis Cache Metrics
def get_redis_cache_metrics():
    try:
        redis_con = get_redis_connection('default')
        info = redis_con.info

        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total_requests = hits + misses
        hit_ratio = (hits / total_requests) if total_requests > 0 else 0

        metrics = {
            "keyspace_hits": hits,
            "keyspace_misses": misses,
            "hit_ratio": round(hit_ratio, 4) if hit_ratio is not None else "N/A"
        }

        logger.info(f"Redis Cache Metrics: {metrics}")
        return metrics

    except Exception as e:
        logger.error(f"Failed to retrieve Redis metrics: {e}")
        return {
            "keyspace_hits": 0,
            "keyspace_misses": 0,
            "hit_ratio": 0
        }
