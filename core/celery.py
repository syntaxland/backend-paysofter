# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create a Celery instance.
app = Celery('core') 

app.conf.enable_utc = False
# app.conf.update(timezone = 'Asia/Kolkata') 
app.conf.update(timezone =  'Africa/Lagos') 

# Load task modules from all registered Django app configs.
# app.config_from_object('django.conf:settings', namespace='CELERY')
app.config_from_object(settings, namespace='CELERY')



# Schedule the process_payouts task to run every 3 minutes (0 */3 * * *)
app.conf.beat_schedule = {
    'process-payouts-every-n-time': {
        'task': 'payout.tasks.process_payouts',
        # 'schedule': crontab(minute='*/1'),
        # 'schedule': crontab(minute=0, hour='*/24'),
        # 'schedule': timedelta(seconds=15),
        'schedule': timedelta(minutes=3),
        # 'schedule': timedelta(hours=1),
        # 'schedule': timedelta(day=1),
    },
}

app.conf.beat_schedule = {
    'seller-payout-payment-processing-everyday': {
        'task': 'payment.tasks.seller_payout_payment',
        # 'schedule': crontab(minute='*/1'),
        # 'schedule': crontab(minute=0, hour='*/24'),
        # 'schedule': timedelta(seconds=15),
        'schedule': timedelta(minutes=5),
        # 'schedule': timedelta(hours=1),
        # 'schedule': timedelta(day=1),
    },
}

app.autodiscover_tasks()
