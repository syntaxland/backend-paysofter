# payout/models.py
from django.db import models
from django.contrib.auth import get_user_model
from transaction.models import Transaction

User = get_user_model() 

 
class Payout(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payout_seller")
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)    
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    commission = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    commission_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False) 
    currency = models.CharField(max_length=3, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    payout_status  = models.BooleanField(default=False) 
    payout_id = models.CharField(max_length=10, unique=True, null=True)
    payment_provider = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - {self.currency} {self.amount} - Payout ID: {self.payout_id}"
