from django.contrib import admin
from . import models


@admin.register(models.Commission)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'timestamp', 
        'payout_payment', 
        'commission_amount', 
        'commission_percentage',
        'currency', 
        'payment_method', 
        'is_paid', 
        'status', 
        'commission_id', 
        'payment_provider', 
    )

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['created_at', 'user', 'balance']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('balance', 'user',)
    #     return readonly_fields
