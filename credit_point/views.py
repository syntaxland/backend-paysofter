# credit_point/views.py
import random
import string
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView
 
from .serializer import CreditPointBalanceSerializer, CreditPointRequestSerializer
# , CreditPointPaymentSerializer, CreditPointEarningSerializer
from .models import CreditPointBalance, CreditPointRequest
# , CreditPointPayment, CreditPointEarning

from django.contrib.auth import get_user_model

User = get_user_model() 


def generate_credit_point_request_ref():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'CPR-'+''.join(random.choices(letters_and_digits, k=7))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_credit_points_balance_view(request):
    try:
        credit_point_balance, created = CreditPointBalance.objects.get_or_create(user=request.user)
        serializer = CreditPointBalanceSerializer(credit_point_balance)
        return Response(serializer.data)
    except CreditPointBalance.DoesNotExist:
        return Response({'detail': 'Credit point balance not found'}, status=status.HTTP_404_NOT_FOUND)
 

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def credit_point_request_view(request):
    user = request.user
    # data = request.data
    # data['user'] = user.id 
    request_ref = generate_credit_point_request_ref()
    print('request_ref:', request_ref) 

    try:
        credit_point_amount = Decimal(request.data.get('credit_point_amount'))
        print('credit_point_amount:', credit_point_amount)

        if credit_point_amount <= 0:
            return Response({'error': 'Credit point amount must be greater than zero.'}, status=status.HTTP_400_BAD_REQUEST)
        
        account_name = request.data.get('account_name')
        account_number = request.data.get('account_number')
        bank_name = request.data.get('bank_name')

        credit_point_request = CreditPointRequest.objects.create(
            user=user,
            credit_point_amount=credit_point_amount,
            account_name=account_name,
            account_number=account_number,
            bank_name=bank_name,
            request_ref=request_ref,
        ) 
        credit_point_request.save()

        credit_point_balance, created = CreditPointBalance.objects.get_or_create(user=user)
        balance = credit_point_balance.balance
        credit_point_balance.balance = 0
        credit_point_balance.save()
        return Response({'success': f'Credit point request submitted successfully. Withdrew NGN {balance}'}, 
                        status=status.HTTP_201_CREATED)
    except CreditPointRequest.DoesNotExist:
            return Response({'detail': 'Credit point request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_credit_point_request_view(request):
    user = request.user
    try:
        credit_point = CreditPointRequest.objects.filter(user=user).order_by('-created_at')
        serializer = CreditPointRequestSerializer(credit_point, many=True)
        return Response(serializer.data)
    except CreditPointRequest.DoesNotExist:
        return Response({'detail': 'Credit point not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def get_all_credit_points_request_view(request):
    try:
        all_credit_points = CreditPointRequest.objects.all().order_by('-created_at')
        serializer = CreditPointRequestSerializer(all_credit_points, many=True)
        return Response(serializer.data)
    except CreditPointRequest.DoesNotExist:
        return Response({'detail': 'Credit point not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_credit_point_earnings(request):
    user = request.user
    try:
        # user_credit_point_earnings = CreditPointEarning.objects.filter(user=user).order_by('-created_at')
        user_credit_point_earnings = CreditPointEarning.objects.filter(user=user).order_by('-created_at').select_related('user', 'order_payment')
        # print('user_credit_point_earnings:', user_credit_point_earnings)
        serializer = CreditPointEarningSerializer(user_credit_point_earnings, many=True)
        # print('user_credit_point_earnings serializer:',serializer)
        return Response(serializer.data)
    except CreditPointEarning.DoesNotExist:
        return Response({'detail': 'Credit point earnings not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_credit_point_payments(request):
    user = request.user
    try:
        credit_point_payments = CreditPointPayment.objects.filter(referrer=user).order_by('-created_at')
        serializer = CreditPointPaymentSerializer(credit_point_payments, many=True)
        return Response(serializer.data)
    except CreditPointPayment.DoesNotExist:
        return Response({'detail': 'Credit point payments not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @permission_classes([IsAdminUser]) 
@permission_classes([IsAuthenticated])
def get_all_credit_point_payments(request):
    try:
        all_credit_points_payments = CreditPointPayment.objects.all().order_by('-created_at')
        serializer = CreditPointPaymentSerializer(all_credit_points_payments, many=True)
        return Response(serializer.data)
    except CreditPointPayment.DoesNotExist:
        return Response({'detail': 'Credit point payments not found'}, status=status.HTTP_404_NOT_FOUND)
