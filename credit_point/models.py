# credit_point/models.py
from django.db import models
# from app.models import Order
# from payment.models import Payment
# from promo.models import Referral
from django.contrib.auth import get_user_model

User = get_user_model()


class CreditPointBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # credit_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class CreditPointEarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_point_earning_user')
    # order_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_point_earnings')
    credit_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class CreditPointRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_point_user')
    # order_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_point_order')
    account_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=10)
    bank_name = models.CharField(max_length=100)
    credit_point_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    request_ref = models.CharField(max_length=10, unique=True, blank=True)
    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    is_delivered = models.BooleanField(default=False)
    delivered_at = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
 

class CreditPointPayment(models.Model):
    # order_payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='credit_point_order_payment')
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="referrer_credit_point_payment")
    credit_points_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    referral_credit_points_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return self.referrer.username if self.referrer else 'No Referrer'

  