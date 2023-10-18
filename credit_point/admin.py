from django.contrib import admin
from . import models


@admin.register(models.CreditPointBalance)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('created_at', 
                    'user', 
                    'balance', )

    # def get_readonly_fields(self, request, obj=None):
    #     readonly_fields = ['created_at', 'user', 'balance']
    #     if obj and obj.is_superuser:
    #         readonly_fields.remove('balance', 'user',)
    #     return readonly_fields


@admin.register(models.CreditPointRequest)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'user', 'account_name', 'account_number', 
                    'bank_name', 'credit_point_amount', 'request_ref', 'is_paid', 'paid_at',
                    'is_delivered', 'delivered_at',)
    search_fields = ('account_number', 'user')  


# @admin.register(models.CreditPointPayment)
# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('created_at', 
#                     'referrer', 
#                     'referral_credit_points_bonus',
#                      'order_payment', )


@admin.register(models.CreditPointEarning)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('created_at',
                     'user', 
                    'credit_points_earned', 
                    # 'order_payment',                  
                      )
