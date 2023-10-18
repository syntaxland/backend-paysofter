# referral/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="referrer")
    referred_users = models.ManyToManyField(User, related_name="referred_users")
    # user_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        referred_users_list = ", ".join(str(user) for user in self.referred_users.all())
        return f'{self.referrer} referred: {referred_users_list}'


class ReferralBonus(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="referrer_bonus")
    referral_credit_points_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
