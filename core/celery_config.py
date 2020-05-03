from __future__ import absolute_import, unicode_literals

import os

from celery import Celery
from celery.schedules import crontab

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch-price-list-every-24-hr': {
        'task': 'mutual_funds.tasks.fetch_price_data',
        'schedule': crontab(minute=0, hour='*/12'),
    },
    'fetch-isin-every-12-hr': {
        'task': 'mutual_funds.tasks.fetch_isin',
        'schedule': crontab(minute=0, hour='*/12'),
    },
}
app.conf.timezone = 'UTC'
