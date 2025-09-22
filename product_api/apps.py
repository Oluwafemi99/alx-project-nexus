from django.apps import AppConfig
import os


class ProductApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'product_api'

    def ready(self):
        import product_api.signals
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError, ProgrammingError

        User = get_user_model()
        try:
            username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
            email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
            password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpass123")

            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                )
                print("✅ Default superuser created:", username)
            else:
                print("ℹ️ Superuser already exists:", username)
        except (OperationalError, ProgrammingError):
            # This happens before migrations are applied
            pass
