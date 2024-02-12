# support/serializers.py
from rest_framework import serializers
from .models import SupportTicket, SupportResponse

     
class SupportTicketSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    account_id = serializers.CharField(source='user.account_id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta: 
        model = SupportTicket
        fields = '__all__'

 
class SupportResponseSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    account_id = serializers.CharField(source='user.account_id', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = SupportResponse
        fields = '__all__'
