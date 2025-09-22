from django.db import migrations
import os


def create_admin(apps, schema_editor):
    User = apps.get_model("product_api", "Users")

    username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "adminpass123")

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        print(f"✅ Default superuser created: {username}")
    else:
        print(f"ℹ️ Superuser already exists: {username}")


class Migration(migrations.Migration):

    dependencies = [
        ("product_api", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]
