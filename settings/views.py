# fund_account/views.py
import random
import string
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView 

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model() 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def select_currency(request):
    user = request.user

    currency = request.data.get('currency')
    print('currency:', currency) 

    try:
        user.selected_currency = currency
        user.save()
        return Response({'detail': f'Success!'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_api_key_status(request):
    user = request.user
    print("user:", user)
    print("Toggling...")
    user.is_api_key_live = not user.is_api_key_live
    user.save()
    print("Toggled!")
    return Response({"detail": "API key status toggled successfully."}, status=status.HTTP_200_OK)
