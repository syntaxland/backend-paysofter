# user_profile/admin.py
from django.contrib import admin
from . import models


@admin.register(models.User)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'id', 
                    'account_id',
                    'security_code',
                    'first_name',  
                    'phone_number',  
                    'is_verified',
                    'referral_code', 
                    'test_api_key',
                    'live_api_key',
                    'is_live_mode',
                    'is_staff', 
                    'is_superuser', 
                    'is_seller', 
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['username', 'account_id', 'test_api_key', 'test_api_secret_key', 'live_api_key', 'live_api_secret_key', 'referral_code', 'referral_link']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('referral_code', 'referral_link')
    #     return readonly_fields

