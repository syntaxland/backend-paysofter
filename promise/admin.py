# promise/admin.py
from django.contrib import admin
from . import models


@admin.register(models.PaysofterPromise)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
                    'promise_id',
                    'seller', 
                    'buyer', 
                    'amount',
                    'currency',
                    'duration',
                    'duration_hours',
                    'expiration_date',
                    'buyer_msg_count', 
                    'seller_msg_count', 
                    'is_active',
                    'buyer_promise_fulfilled',
                    'seller_fulfilled_promise',  
                    'status',  
                    'is_delivered',
                    'is_success',
                    'is_cancelled',
                    'is_settle_conflict_activated', 
                    'settle_conflict_charges',
                    'payment_method',
                    'payment_provider',
                    'timestamp',
                    )


@admin.register(models.TestPaysofterPromise)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
                    'promise_id',
                    'seller', 
                    'buyer_email', 
                    'amount',
                    'currency',
                    'duration',
                    'duration_hours',
                    'expiration_date',
                    'buyer_msg_count', 
                    'seller_msg_count', 
                    'is_active',
                    'buyer_promise_fulfilled',
                    'seller_fulfilled_promise',  
                    'status',  
                    'is_delivered',
                    'is_success',
                    'is_cancelled',
                    'is_settle_conflict_activated', 
                    'settle_conflict_charges',
                    'payment_method',
                    'payment_provider',
                    'timestamp',
                    )


@admin.register(models.PromiseMessage)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
                    'user',
                    'seller', 
                    'buyer', 
                    'promise_message', 
                    'message', 
                    'timestamp',                    
                    )
