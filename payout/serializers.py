# payout/serializers.py
from rest_framework import serializers
from .models import Payout
from transaction.serializers import TransactionSerializer
from django.contrib.auth import get_user_model

User = get_user_model() 


class PayoutSerializer(serializers.ModelSerializer):
    transaction = TransactionSerializer()
    payment_id = serializers.CharField(source='transaction.payment_id', read_only=True)
    # first_name = serializers.CharField(source='seller.first_name', read_only=True)
    # last_name = serializers.CharField(source='seller.last_name', read_only=True)
    seller_email = serializers.CharField(source='seller.email', read_only=True)

    class Meta:
        model = Payout 
        fields = '__all__' 
