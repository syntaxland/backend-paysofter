# promise/serializers.py

from rest_framework import serializers
from .models import PaysofterPromise, PromiseMessage
from django.contrib.auth import get_user_model

User = get_user_model() 

 
class PaysofterPromiseSerializer(serializers.ModelSerializer):
    seller_email = serializers.CharField(source='seller.email', read_only=True) 
    buyer_email = serializers.CharField(source='buyer.email', read_only=True)
    seller_account_id = serializers.CharField(source='seller.account_id', read_only=True) 
    buyer_account_id = serializers.CharField(source='buyer.account_id', read_only=True)

    class Meta:
        model = PaysofterPromise
        fields = '__all__'


class PromiseMessageSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)  
    seller_first_name = serializers.CharField(source='seller.first_name', read_only=True) 
    buyer_first_name = serializers.CharField(source='buyer.first_name', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True) 
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)

    class Meta:
        model = PromiseMessage
        fields = '__all__'


