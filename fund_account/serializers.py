# fund_account/serializers.py

from rest_framework import serializers
from .models import FundAccount, AccountFundBalance, DebitAccountFund
from django.contrib.auth import get_user_model

User = get_user_model() 

 
class FundAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = FundAccount
        fields = '__all__'


class AccountFundBalanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountFundBalance
        fields = '__all__'

 
class DebitAccountFundSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = DebitAccountFund
        fields = '__all__'

class OtpDataSerializer(serializers.Serializer):
    otp = serializers.CharField()
    amount = serializers.CharField()
    account_id = serializers.CharField()
    currency = serializers.CharField()
