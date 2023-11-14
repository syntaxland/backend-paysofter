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
                    'buyer_promise_fulfilled',
                    'seller_fulfilled_promise',  
                    'status',  
                    'is_success',
                    'payment_method',
                    'payment_provider',
                    'timestamp',
                    )


@admin.register(models.PromiseMessage)
class AuthorAdmin(admin.ModelAdmin):
    list_display = (
                    'user',
                    'promise_message', 
                    'message', 
                    'timestamp',                    
                    )
