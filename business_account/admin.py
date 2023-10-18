# business_account/admin.py
from django.contrib import admin
from . import models


@admin.register(models.BusinessAccount)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('seller', 
                    'business_name', 
                    'trading_name',
                    'business_reg_num',  
                    'business_address',  
                    'business_type',
                    'staff_size',
                    'business_industry', 
                    'business_category',
                    'business_description',  
                    'business_website',  
                    'country',
                    'created_at',
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'payment_method',  'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_success', 'is_paid')
    #     return readonly_fields


@admin.register(models.BankAccount)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('seller', 
                    'bank_name', 
                    'account_name',
                    'bank_account_number',  
                    'created_at',  
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['amount', 'currency', 'payment_method',  'timestamp']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('is_success', 'is_paid')
    #     return readonly_fields
