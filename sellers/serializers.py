# sellers/serializers.py
from rest_framework import serializers
from .models import SellerAccount, BusinessOwnerDetail, BankVerificationNumber, SellerPhoto, BankAccount, BusinessStatus, UsdBankAccount


class SellerAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerAccount
        fields = '__all__'


class BusinessStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessStatus
        fields = '__all__'
        extra_kwargs = {'business_reg_cert': {'required': True}}


class BusinessOwnerDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessOwnerDetail
        fields = '__all__'
        extra_kwargs = {'id_card_image': {'required': True}, 'proof_of_address': {'required': True}}


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = '__all__'
        # extra_kwargs = {'photo': {'required': True}}


class UsdBankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsdBankAccount
        fields = '__all__'


class BankVerificationNumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankVerificationNumber
        fields = '__all__'


class SellerPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerPhoto
        fields = '__all__'
        extra_kwargs = {'photo': {'required': True}}
