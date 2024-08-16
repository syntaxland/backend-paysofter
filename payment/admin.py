from django.contrib import admin
from . import models


@admin.register(models.PaymentLink)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp',
        'seller',
        'payment_name',
        'amount',
        'currency',
        'show_promise_option',
        'show_fund_option',
        'show_card_option',
        'show_buyer_name',
        'show_buyer_phone',
        'payment_link',
        'description',
    )  
    search_fields = ('payment_id', 'transaction_id')
