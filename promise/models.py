# promise/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CURRENCY_CHOICES = (
        ('NGN', 'Nigerian Naira'),
        ('USD', 'United States Dollar'),
        ('GBP', 'British Pound Sterling'),
        ('EUR', 'Euro'),
        ('JPY', 'Japanese Yen'),
        ('CAD', 'Canadian Dollar'),
        ('AUD', 'Australian Dollar'),
        ('INR', 'Indian Rupee'),
        ('CNY', 'Chinese Yuan'),
        ('ZAR', 'South African Rand'),
        ('BRL', 'Brazilian Real'),
        ('KES', 'Kenyan Shilling'),
        ('GHS', 'Ghanaian Cedi'),
        ('AED', 'United Arab Emirates Dirham'),
        ('SAR', 'Saudi Riyal'),
        ('GBP', 'British Pound Sterling'),
    )

PAYMENT_METHOD_CHOICES = (
        ('debit_card', 'Debit Card'),
        ('paysofter_account_fund', 'Paysofter Account Fund'),
        ('paysofter_promise', 'Paysofter Promise'),
        ('bank', 'Bank'),
        ('transfer', 'Transfer'),
        ('qrcode', 'QR COde'),
        ('USSD', 'USSD'),
    )

PAYMENT_PROVIDER_CHOICES = (
        ('paysofter', 'Paysofter'),
        ('mastercard', 'Mastercard'),
        ('verve', 'Verve'),
        ('visa', 'Visa'),
        ('gtb', 'GTB'),
        ('fidelity', 'Fidelity'),
    )

PROMISE_STATUS_CHOICES = (
        ('fulfilled', 'Fulfilled'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )

PROMISE_DURATION_CHOICES = (
        ('1day', '1 day'),
        ('2days', 'Less than 2 days'),
        ('3days', 'Less than 3 days'),
        ('1week', 'Less than 1 week'),
        ('2week', 'Less than 2 weeks'),
        ('1month', 'Less than 1 month'),
    )


class PaysofterPromise(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_seller")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_payer")
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    duration = models.CharField(max_length=100, choices=PROMISE_DURATION_CHOICES, default='1day', null=True, blank=True)
    status = models.CharField(max_length=100, choices=PROMISE_STATUS_CHOICES, null=True, blank=True)
    is_success = models.BooleanField(default=False)
    payer_promise_fulfilled = models.BooleanField(default=False)
    seller_fulfilled_promise = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_provider = models.CharField(max_length=100, choices=PAYMENT_PROVIDER_CHOICES)
    promise_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.seller} - {self.payer} - {self.amount}" 
