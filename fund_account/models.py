# fund_account/models.py
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
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
        # ('USSD', 'USSD'),
        ('paypal', 'PayPal'),
        ('google_pay', 'Google Pay'),
        ('apple_pay', 'Apple Pay'),
    )

PAYMENT_PROVIDER_CHOICES = (
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('gtb', 'GTB'),
        ('fidelity', 'Fidelity'),
    )

# MAX_WITHDRAWAL_CHOICES = (
#         ('10000', 'Less than 10,000'),
#         ('100000', 'Less than 100,000'),
#         ('1000000', 'Less than 1,000,000'),
#         ('2000000', 'Less than 2,000,000'),
#         ('5000000', 'Less than 5,000,000'),
#         ('10000000', 'Less than 10,000,000'),
#         ('100000000', 'More than 10,000,000'),
#     )

MAX_WITHDRAWAL_CHOICES = (
    (10000, 'Less than 10,000'),
    (100000, 'Less than 100,000'),
    (500000, 'Less than 500,000'),
    (1000000, 'Less than 1,000,000'),
    (2000000, 'Less than 2,000,000'),
    (5000000, 'Less than 5,000,000'),
    (10000000, 'Less than 10,000,000'),
    (1000000000, 'More than 10,000,000'),
)


class FundAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fund_account_user")
    amount = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    is_success = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_provider = models.CharField(max_length=50, choices=PAYMENT_PROVIDER_CHOICES, null=True, blank=True)
    fund_account_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return f"{self.user} - {self.amount}"


class AccountFundBalance(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fund_account_balance_user")
    balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    max_withdrawal = models.DecimalField(max_digits=16, decimal_places=2, default=2000000, choices=MAX_WITHDRAWAL_CHOICES, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -  {self.balance}" 


class DebitAccountFund(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="fund_account_debit_user")
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, null=True, blank=True)
    is_success = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    payment_provider = models.CharField(max_length=50, choices=PAYMENT_PROVIDER_CHOICES)
    debit_account_id = models.CharField(max_length=10, unique=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} -  {self.amount}" 


class FundAccountCreditCard(models.Model):
    fund_account = models.ForeignKey(FundAccount, on_delete=models.SET_NULL, null=True, blank=True, related_name="fund_account_credit_card")
    card_number = models.CharField(max_length=100, null=True, blank=True)
    expiration_month_year = models.CharField(max_length=100, null=True, blank=True)
    cvv = models.CharField(max_length=100, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
