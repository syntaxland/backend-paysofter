# transaction/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model() 
 

class Transaction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="transaction_seller")
    buyer_email = models.CharField(max_length=225, null=True, blank=True) 
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, editable=False)
    currency = models.CharField(max_length=3, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    payout_status = models.BooleanField(default=False) 
    is_success = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=20, unique=True, null=True)
    transaction_id = models.CharField(max_length=20, unique=True, null=True) 
    payment_provider = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - NGN {self.amount} - Payment ID: {self.payment_id}"

 
class TestTransaction(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="test_transaction_seller")
    buyer_email = models.CharField(max_length=100, null=True, blank=True) 
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, editable=False)
    currency = models.CharField(max_length=3, null=True, blank=True)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    is_success = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=14, unique=True, null=True)
    transaction_id = models.CharField(max_length=14, unique=True, null=True)
    payment_provider = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - NGN {self.amount} - Payment ID: {self.payment_id}"

 
class TransactionCreditCard(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True, blank=True)
    card_number = models.CharField(max_length=100, null=True, blank=True)
    expiration_month = models.CharField(max_length=100, null=True, blank=True)
    expiration_year = models.CharField(max_length=100, null=True, blank=True)
    expiration_month_year = models.CharField(max_length=100, null=True, blank=True)
    cvv = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
