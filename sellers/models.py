from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SellerAccount(models.Model):
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="business_account_seller")
    business_name = models.CharField(max_length=100, null=True, blank=True)
    trading_name = models.CharField(max_length=100, null=True, blank=True)
    business_reg_num = models.CharField(max_length=50, null=True, blank=True)
    business_address = models.CharField(max_length=225, null=True, blank=True)

    BUSINESS_TYPE_CHOICES = [
        ('registered', 'Registered'),
        ('unregistered', 'Unregistered'), 
    ]
    business_type = models.CharField(
        max_length=225,
        null=True,
        blank=True,
        choices=BUSINESS_TYPE_CHOICES,  
    )

    STAFF_SIZE_CHOICES = [
        ('small', 'Small (1-50 employees)'),
        ('medium', 'Medium (51-250 employees)'),
        ('large', 'Large (251+ employees)'),
    ]
    staff_size = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=STAFF_SIZE_CHOICES,
    )

    BUSINESS_INDUSTRY_CHOICES = [
        ('it', 'Information Technology'),
        ('healthcare', 'Healthcare'),
        # Add other industry choices as needed
    ]
    business_industry = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=BUSINESS_INDUSTRY_CHOICES,
    )

    BUSINESS_CATEGORY_CHOICES = [
        ('startup', 'Startup'),
        ('small_business', 'Small Business'),
        # Add other category choices as needed
    ]
    business_category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=BUSINESS_CATEGORY_CHOICES,
    )

    business_description = models.TextField(max_length=225, null=True, blank=True)
    business_website = models.CharField(max_length=225, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business_name}"
