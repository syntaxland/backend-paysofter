# credit_point/serializers.py
from rest_framework import serializers
from .models import CreditPointBalance, CreditPointRequest, CreditPointPayment, CreditPointEarning
from user_profile.serializers import UserSerializer
from payment.serializers import PaymentSerializer
from django.contrib.auth import get_user_model

User = get_user_model() 


class CreditPointRequestSerializer(serializers.ModelSerializer):
    email = serializers.CharField(source='user.email', read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    class Meta:
        model = CreditPointRequest
        fields = '__all__'


class CreditPointBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditPointBalance
        fields = "__all__"


# class CreditPointEarningSerializer(serializers.ModelSerializer):
#     order_payment = PaymentSerializer()
#     # user = UserSerializer()
#     order_id = serializers.CharField(source='order_payment.order.order_id', read_only=True)
#     # email = serializers.CharField(source='user.email', read_only=True)
#     first_name = serializers.CharField(source='order_payment.user.first_name', read_only=True)
#     last_name = serializers.CharField(source='order_payment.user.last_name', read_only=True)
#     class Meta:
#         model = CreditPointEarning
#         fields = "__all__"


# class CreditPointPaymentSerializer(serializers.ModelSerializer): 
#     order_payment = PaymentSerializer()
#     order_id = serializers.CharField(source='order_payment.order.order_id', read_only=True)
#     referred_first_name = serializers.CharField(source='order_payment.user.first_name', read_only=True)
#     referred_last_name = serializers.CharField(source='order_payment.user.last_name', read_only=True)
#     referred_email = serializers.CharField(source='order_payment.user.email', read_only=True)

#     referrer = UserSerializer()
#     referrer_email = serializers.CharField(source='referrer.email', read_only=True)
#     referrer_first_name = serializers.CharField(source='referrer.first_name', read_only=True)
#     referrer_last_name = serializers.CharField(source='referrer.last_name', read_only=True)


#     class Meta:
#         model = CreditPointPayment
#         fields = "__all__"
