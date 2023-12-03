from django.contrib import admin
from . import models


@admin.register(models.SellerAccount)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'seller',
        'business_name',
        'trading_name',
        # 'is_business_registered',
        'business_reg_num',
        'business_address',
        'business_type',
        'staff_size',
        'business_industry',
        'business_category',
        'business_description',
        'business_phone',
        'business_email',
        'support_email',
        'business_website',
        'country',
    )  

@admin.register(models.BusinessStatus)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'seller',
        'is_business_registered',
        'business_status',
        'business_name',
        'business_reg_num',
        'business_reg_cert',
    )  

@admin.register(models.BusinessOwnerDetail)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'created_at',
        'seller',
        'director_name',
        'id_type',
        'id_number',
        'id_card_image',
        'dob',
        'address',
        'proof_of_address',
    )  


@admin.register(models.BankAccount)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'seller',
        'account_name',
        'bank_account_number',
        'bank_name',
        'created_at',
    )  


@admin.register(models.BankVerificationNumber)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'seller',
        'bvn',
        'created_at',
    )  


@admin.register(models.SellerPhoto)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
        'seller',
        'photo',
        'created_at',
    )  
