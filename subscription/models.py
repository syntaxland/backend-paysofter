# subscription/models.py
from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    plan = models.CharField(max_length=100)
    status = models.CharField(max_length=20)  # e.g., "active", "canceled"
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
