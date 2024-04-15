# user_profile/admin.py
from django.contrib import admin
from . import models


@admin.register(models.User)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('email', 'last_login', 
                    'created_at', 'id', 
                    'account_id',
                    'security_code',
                    'first_name',  
                    'phone_number',  
                    'is_verified',
                    'selected_currency', 
                    'referral_code', 
                    'test_api_key',
                    'live_api_key',
                    'is_api_key_live',
                    'is_staff', 
                    'is_superuser', 
                    'is_seller', 
                    'user_is_not_active', 
                    'is_user_live_banned', 
                    )
    
    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['username', 'account_id', 'test_api_key', 'test_api_secret_key', 'live_api_key', 'live_api_secret_key', 'referral_code', 'referral_link']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('referral_code', 'referral_link')
    #     return readonly_fields

