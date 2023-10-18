# payment/serializers.py

from rest_framework import serializers
from .models import PayoutPayment
from django.contrib.auth import get_user_model

User = get_user_model() 

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutPayment
        fields = '__all__'


