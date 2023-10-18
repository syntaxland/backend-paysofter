# payout/admin.py
from django.contrib import admin
from . import models


@admin.register(models.Payout)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('seller', 'transaction', 'amount', 
                    'currency',
                    'payment_method',  
                    'is_approved',  
                    'is_paid',
                    'payout_status', 
                    'payout_id',
                    'payment_provider',
                    'timestamp',
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'payment_method', 'is_approved', 'is_paid', 'payout_status', 'payout_id', 'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_approved', 'is_paid')
    #     return readonly_fields

