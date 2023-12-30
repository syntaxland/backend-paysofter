# fund_account/serializers.py

from rest_framework import serializers
from .models import (FundAccount, AccountFundBalance, 
                     DebitAccountFund,
                     UsdAccountFundBalance,
                    FundUsdAccount,
                    DebitUsdAccountFund,
                    
                  )
from django.contrib.auth import get_user_model

User = get_user_model() 

 
class FundAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True) 
    class Meta:
        model = FundAccount
        fields = '__all__'


class AccountFundBalanceSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True) 
    account_id = serializers.CharField(source='user.account_id', read_only=True) 
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


class UsdAccountFundBalanceSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True) 
    account_id = serializers.CharField(source='user.account_id', read_only=True) 
    class Meta:
        model = UsdAccountFundBalance
        fields = '__all__'


class FundUsdAccountSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True) 
    class Meta:
        model = FundUsdAccount
        fields = '__all__'

 
class DebitUsdAccountFundFundSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True)
    class Meta:
        model = DebitUsdAccountFund
        fields = '__all__'
