# product_api/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_project_nexus.settings')

app = Celery('your_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
