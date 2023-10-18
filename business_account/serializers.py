# business_account/serializers.py

from rest_framework import serializers
from .models import BusinessAccount, BankAccount
from django.contrib.auth import get_user_model

User = get_user_model() 

class BusinessAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessAccount
        fields = '__all__'


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
