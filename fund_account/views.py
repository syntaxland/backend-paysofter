# fund_account/views.py
import random
import string
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

from .serializers import FundAccountSerializer, AccountFundBalanceSerializer, DebitAccountFundSerializer
from .models import FundAccount, AccountFundBalance, DebitAccountFund

from django.contrib.auth import get_user_model

User = get_user_model() 


def generate_fund_account_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'AFD'+''.join(random.choices(letters_and_digits, k=7))
 

def generate_debit_account_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'DBF'+''.join(random.choices(letters_and_digits, k=7))


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def fund_user_account_view(request):
    user = request.user
    # data = request.data
    # data['user'] = user.id 
    fund_account_id = generate_fund_account_id()
    print('fund_account_id:', fund_account_id)

    try:
        amount = Decimal(request.data.get('amount'))
        currency = request.data.get('currency')
        payment_method = request.data.get('payment_method')
        payment_provider = request.data.get('payment_provider')

        fund_account = FundAccount.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            payment_provider=payment_provider,
            fund_account_id=fund_account_id,
        ) 
        fund_account.save()

        fund_account_balance, created = AccountFundBalance.objects.get_or_create(user=user)
        balance = fund_account_balance.balance
        fund_account_balance.balance += amount 
        fund_account_balance.save()
        return Response({'success': f'Fund account request submitted successfully. Old Bal: NGN {balance}'}, 
                        status=status.HTTP_201_CREATED)
    except FundAccount.DoesNotExist:
            return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_account_fund_balance(request):
    try:
        account_fund_balance, created = AccountFundBalance.objects.get_or_create(user=request.user)
        serializer = AccountFundBalanceSerializer(account_fund_balance)
        return Response(serializer.data)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Fund account balance not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_account_funds(request):
    user = request.user
    try:
        account_funds = FundAccount.objects.filter(user=user).order_by('-timestamp')
        serializer = FundAccountSerializer(account_funds, many=True)
        return Response(serializer.data)
    except FundAccount.DoesNotExist:
        return Response({'detail': 'Fund account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])   
def debit_user_fund_account(request):
    # user = request.user
    # print('user:',user)
    debit_account_id = generate_debit_account_id()
    print('fund_account_id:', debit_account_id) 

    amount = request.data.get('amount')
    if amount is None:
        return Response({'detail': 'Amount is required in the request data.'}, status=status.HTTP_400_BAD_REQUEST)
    amount = Decimal(amount)

    currency = request.data.get('currency')
    # payment_method = request.data.get('payment_method')
    # payment_provider = request.data.get('payment_provider')
    account_id = request.data.get('account_id')
    otp = request.data.get('otp')
    print('amount, account_id', amount, account_id)

    # user = User.objects.get(account_id=account_id)
    # if not user:
    #     return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

    print('user:', user)

    try:
        account_balance, created = AccountFundBalance.objects.get_or_create(user=user)

        balance = account_balance.balance
        print('old balance:', balance)

        if balance < amount: 
            return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
        account_balance.balance -= amount 
        account_balance.save()
        print('new balance:', account_balance.balance)

        debit_fund_account = DebitAccountFund.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            # payment_method=payment_method,
            # payment_provider=payment_provider,
            debit_account_id=debit_account_id,
        ) 
        debit_fund_account.save()

        return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
    except DebitAccountFund.DoesNotExist:
            return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_debits(request):
    user = request.user
    try:
        account_debits = DebitAccountFund.objects.filter(user=user).order_by('-timestamp')
        serializer = DebitAccountFundSerializer(account_debits, many=True)
        return Response(serializer.data)
    except FundAccount.DoesNotExist:
        return Response({'detail': 'Debit account not found'}, status=status.HTTP_404_NOT_FOUND)
