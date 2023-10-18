from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class SendBuyerEmail(models.Model):
    paysofter_email = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paysofter_send_buyer_email')
    buyer_email = models.EmailField(max_length=255, null=True, blank=True)
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(max_length=5000, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    

class SendSellerEmail(models.Model):
    paysofter_email = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='paysofter_send_seller_email')
    seller = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='seller')
    subject = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(max_length=5000, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
