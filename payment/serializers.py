# payment/serializers.py

from rest_framework import serializers
from .models import PayoutPayment, PaymentLink
from django.contrib.auth import get_user_model

User = get_user_model() 


class PaymentLinkSerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    # test_api_key = serializers.CharField(source='seller.test_api_key', read_only=True) 
    # live_api_key = serializers.CharField(source='seller.live_api_key', read_only=True)
    # is_api_key_live = serializers.CharField(source='seller.is_api_key_live', read_only=True)
    class Meta:
        model = PaymentLink
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutPayment
        fields = '__all__'


