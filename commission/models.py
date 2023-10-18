# commission/models.py
from django.db import models
from django.contrib.auth import get_user_model
from payment.models import PayoutPayment

User = get_user_model() 

COMMISSION_STATUS = (
        ('success', 'Success'),
        ('faild', 'Faild'),
    )


class Commission(models.Model):
    payout_payment = models.ForeignKey(PayoutPayment, on_delete=models.SET_NULL, null=True, blank=True)    
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    commission_percentage = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) 
    currency = models.CharField(max_length=3, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    is_paid  = models.BooleanField(default=False)
    status = models.CharField(max_length=100, null=True, blank=True, choices=COMMISSION_STATUS)
    commission_id = models.CharField(max_length=10, unique=True, null=True)
    payment_provider = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f" {self.commission_amount} - {self.payout_payment} - Commission ID: {self.commission_id}"
