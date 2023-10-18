# webhook_event/models.py
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 


class WebhookEvent(models.Model):
    event_type = models.CharField(max_length=100)
    data = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
