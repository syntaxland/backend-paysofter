# fund_account/admin.py
from django.contrib import admin
from . import models


@admin.register(models.CurrencyChoice)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user', 
                    'currency', 
                    'timestamp',
                    )
