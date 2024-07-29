# transaction/serializers.py
from rest_framework import serializers
from .models import Transaction, TransactionCreditCard, TestTransaction
from user_profile.serializers import UserSerializer
from django.contrib.auth import get_user_model

User = get_user_model() 


class TransactionSerializer(serializers.ModelSerializer):
    # seller = UserSerializer()
    first_name = serializers.CharField(source='seller.first_name', read_only=True)
    last_name = serializers.CharField(source='seller.last_name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)

    class Meta:
        model = Transaction 
        fields = '__all__'


class TestTransactionSerializer(serializers.ModelSerializer):
    # seller = UserSerializer()
    first_name = serializers.CharField(source='seller.first_name', read_only=True)
    last_name = serializers.CharField(source='seller.last_name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)

    class Meta:
        model = TestTransaction 
        fields = '__all__'

class TransactionCreditCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionCreditCard
        fields = '__all__'
