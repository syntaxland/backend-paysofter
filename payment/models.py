# payment/models.py
from django.db import models
from django.contrib.auth import get_user_model
from payout.models import Payout

User = get_user_model() 
 

class PayoutPayment(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="payout_payment_seller") 
    payout = models.ForeignKey(Payout, on_delete=models.SET_NULL, null=True, blank=True, related_name="payout_payment")    
    
    bank_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100)
    bank_account_number = models.CharField(max_length=10)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, editable=False)
    
    currency = models.CharField(max_length=3)  
    payment_method = models.CharField(max_length=50) 
    is_paid = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    payout_payment_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - {self.total_amount} - {self.payout_payment_id}"
