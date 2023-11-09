# fund_account/admin.py
from django.contrib import admin
from . import models


@admin.register(models.FundAccount)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 
                    'amount', 
                    'currency',
                    'payment_method',  
                    'is_success',  
                    'fund_account_id',
                    'timestamp',
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'fund_account_id',  'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_success', 'fund_account_id')
    #     return readonly_fields

@admin.register(models.AccountFundBalance)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 
                    'balance', 
                    'max_withdrawal', 
                    'is_active',
                    'timestamp',
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'fund_account_id',  'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_success', 'fund_account_id')
    #     return readonly_fields


@admin.register(models.DebitAccountFund)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 
                    'amount', 
                    'currency',
                    'payment_method',  
                    'is_success',  
                    'debit_account_id',
                    'timestamp',
                    )
     
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'fund_account_id',  'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_success', 'fund_account_id')
    #     return readonly_fields
