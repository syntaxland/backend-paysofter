# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') 

app = Celery('core') 
app.conf.enable_utc = False
app.conf.update(timezone =  'Africa/Lagos') 
app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    'process-payouts-every-n-time': {
        'task': 'payout.tasks.process_payouts',
        'schedule': timedelta(minutes=3),
    },
    'seller-payout-payment-processing-everyday': {
        'task': 'payment.tasks.seller_payout_payment',
        'schedule': timedelta(minutes=5),
    },
    'update-security-codes-every-hour': {
        'task': 'user_profile.tasks.update_security_codes_for_users',
        # 'schedule': timedelta(hours=1),
        'schedule': timedelta(minutes=5),
    },
    'process-promise-transactions-every-n-time': {
        'task': 'promise.tasks.process_promise_transactions',
        'schedule': timedelta(minutes=5),
    },
    'close-resolved-tickets': {
        'task': 'support.tasks.close_resolved_tickets',
        'schedule': timedelta(minutes=1),
    },
}

app.autodiscover_tasks()
