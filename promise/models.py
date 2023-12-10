# promise/models.py
from datetime import timedelta, datetime
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

CURRENCY_CHOICES = (
        ('NGN', 'NGN'),
        ('USD', 'USD'),
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
    )

PAYMENT_METHOD_CHOICES = (
        ('Debit Card', 'Debit Card'),
        ('Paysofter Account Fund', 'Paysofter Account Fund'),
        ('Paysofter Promise', 'Paysofter Promise'),
        ('Bank', 'Bank'),
        ('Transfer', 'Transfer'),
        ('QR COde', 'QR COde'),
        ('USSD', 'USSD'),
    )

PAYMENT_PROVIDER_CHOICES = (
        ('Paysofter', 'Paysofter'),
        ('Mastercard', 'Mastercard'),
        ('Verve', 'Verve'),
        ('Visa', 'Visa'),
        ('GTB', 'GTB'),
        ('Fidelity', 'Fidelity'),
    )

PROMISE_DURATION_CHOICES = (
        ('0 day', '0 day'),
        ('Within 1 day', 'Within 1 day'),
        ('2 days', 'Less than 2 days'),
        ('3 days', 'Less than 3 days'),
        ('5 days', 'Less than 5 days'),
        ('1 week', 'Less than 1 week'),
        ('2 weeks', 'Less than 2 weeks'),
        ('1 month', 'Less than 1 month'),
    )

PROMISE_STATUS_CHOICES = (
        ('Processing', 'Processing'),
        ('Fulfilled', 'Fulfilled'),
        ('Failed', 'Failed'),
        ('Cancelled', 'Cancelled'),
    )

class PaysofterPromise(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_seller")
    buyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_payer")
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True, editable=False)
    currency = models.CharField(max_length=16, choices=CURRENCY_CHOICES, default='NGN', null=True, blank=True)
    duration = models.CharField(max_length=100, choices=PROMISE_DURATION_CHOICES, default='Within 1 day', null=True, blank=True)
    duration_hours = models.DurationField(null=True, blank=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=100, choices=PROMISE_STATUS_CHOICES, default='Processing', null=True, blank=True)
    is_success = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_delivered = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    buyer_promise_fulfilled = models.BooleanField(default=False)
    seller_fulfilled_promise = models.BooleanField(default=False)
    is_settle_conflict_activated = models.BooleanField(default=False)
    settle_conflict_charges = models.DecimalField(max_digits=16, decimal_places=2, default=0, null=True, blank=True, editable=False)
    service_charge = models.DecimalField(max_digits=16, decimal_places=2, default=0, null=True, blank=True, editable=False)
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_provider = models.CharField(max_length=100, choices=PAYMENT_PROVIDER_CHOICES)
    promise_id = models.CharField(max_length=10, unique=True, null=True, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def save(self, *args, **kwargs):
        if self.duration:
            if self.duration == '0 day':
                self.duration_hours = timedelta(hours=0)
            elif self.duration == 'Within 1 day':
                self.duration_hours = timedelta(hours=24)
            elif self.duration == '2 days':
                self.duration_hours = timedelta(days=2)
            elif self.duration == '3 days':
                self.duration_hours = timedelta(days=3)
            elif self.duration == '5 days':
                self.duration_hours = timedelta(days=5)
            elif self.duration == '1 week':
                self.duration_hours = timedelta(weeks=1)
            elif self.duration == '2 weeks':
                self.duration_hours = timedelta(weeks=2)
            elif self.duration == '1 month':
                self.duration_hours = timedelta(days=30)  

            self.expiration_date = datetime.now() + self.duration_hours
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.promise_id}" 
    

class PromiseMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="promise_message_user")
    promise_message = models.ForeignKey(PaysofterPromise, on_delete=models.CASCADE, related_name='promise_message', blank=True, null=True)
    message = models.TextField(max_length=225, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return f"{self.user} | {self.promise_message}" 
