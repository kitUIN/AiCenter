import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')

from django.conf import settings
from celery import platforms

django.setup()
from celery import Celery

app = Celery(f"application")

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
platforms.C_FORCE_ROOT = True

# nohup celery -A application worker --loglevel=INFO -n worker_io@$(date +%s%N | cut -b1-13) -c 100 -P gevent -Q io &
