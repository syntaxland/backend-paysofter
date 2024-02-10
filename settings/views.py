# fund_account/views.py
import random
import string
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

# from .models import (CurrencyChoice, 
#                     )

# from .serializers import (CurrencyChoiceSerializer, 
#                           )

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


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def get_selected_currency(request):
#     user = request.user
#     try:
#         selected_currency = CurrencyChoice.objects.filter(user=user).order_by('-timestamp')
#         serializer = CurrencyChoiceSerializer(selected_currency, many=True)
#         return Response(serializer.data)
#     except CurrencyChoice.DoesNotExist:
#         return Response({'detail': 'Currency not found'}, status=status.HTTP_404_NOT_FOUND)
