from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'food_waste_management.settings')
app = Celery('food_waste_management')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()