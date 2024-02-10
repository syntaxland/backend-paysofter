# settings/models.py
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


class CurrencyChoice(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="selected_currency_user")
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES,  default='USD', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
