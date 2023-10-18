from django.contrib import admin
from . import models


@admin.register(models.Transaction)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'seller',
        'buyer_email',
        'amount',
        'currency',
        'payment_method',
        'is_success',
        'is_approved',
        'payout_status',
        'payment_id',
        'transaction_id',
        'payment_provider',
    )  
    search_fields = ('payment_id', 'transaction_id')


@admin.register(models.TransactionCreditCard)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'card_number',
        # 'expiration_month',
        'expiration_month_year',
        # 'expiration_month_yaer',
        'cvv',
        'transaction',
    )  
 