from django.apps import AppConfig


class ProductApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product_api'

    def ready(self):
        import product_api.signals
