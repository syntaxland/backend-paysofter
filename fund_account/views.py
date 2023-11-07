# fund_account/views.py
import random
import string
from decimal import Decimal

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException 

from .serializers import FundAccountSerializer, AccountFundBalanceSerializer, DebitAccountFundSerializer, OtpDataSerializer
from .models import FundAccount, AccountFundBalance, DebitAccountFund

# from send_email_otp.serializers import EmailOTPSerializer
from send_email_otp.models import EmailOtp
from django.conf import settings
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


def format_email(email):
    if '@' in email:
        parts = email.split('@')
        if len(parts[0]) < 2 or len(parts[1]) < 2:
            # If the username or domain is too short, don't modify the email
            return email
        else:
            username = parts[0][0] + '*' * (len(parts[0]) - 2) + parts[0][-1]
            domain = parts[1][0] + '*' * (len(parts[1]) - 2) + parts[1][-1]
            return f"{username}@{domain}"
    else:
        # If there's no '@' character in the email, don't modify it
        return email


@api_view(['POST'])
@permission_classes([AllowAny])   
def debit_user_fund_account(request):
    
    account_id = request.data.get('account_id')
    print('account_id', account_id)

    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
    print('user:', user)

    payer_email = user.email
    first_name = user.first_name
    formatted_payer_email = format_email(payer_email)
    print('payer_email:', payer_email, 'first_name:', first_name, 'formatted_payer_email:', formatted_payer_email)

    try:
        send_payer_account_fund_otp(request, payer_email, first_name)
    except Exception as e:
        print(e)
        # return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'detail': 'Email sent.', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)
    

def send_payer_account_fund_otp(request, payer_email, first_name):
    print('first_name:', first_name, 'payer_email:',  payer_email)

    email_otp, created = EmailOtp.objects.get_or_create(email=payer_email)
    email_otp.generate_email_otp()
    print('email_otp:', email_otp, "email_otp:", email_otp.email_otp)

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    # Sending email
    subject = "Account Fund Payment OTP"
    print("\nSending email OTP...")
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>OTP Account Fund Payment</title>
        </head>
        <body>
            <p>Dear {first_name.title()},</p>
            <p>To complete this payment using Paysofter Account Fund, please use the OTP provided below:</p>
            <h2>OTP: {email_otp.email_otp}</h2>
            <p>This OTP is valid for 10 minutes.</p>
            <p>If you didn't request this OTP, please ignore it.</p>
            <p>Best regards,</p>
            <p>Paysofter Inc.</p>
        </body>
        </html>
    """ 
    sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
    sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
    sender = {"name": sender_name, "email": sender_email}
    to = [{"email": payer_email, "name": first_name}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content, 
        sender=sender,
        subject=subject
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent!")
    except ApiException as e:
        print(e)
        return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_account_debit_email_otp(request):
    data = request.data
    print('data:', data)

    otp_data = request.data.get('otpData', {}) 
    otp = otp_data.get('otp')
    amount = otp_data.get('amount')
    account_id = otp_data.get('account_id')
    currency = otp_data.get('currency')


    # otp = request.data.get('otp')
    # amount = request.data.get('amount')
    # account_id = request.data.get('account_id')
    # currency = request.data.get('currency')
    debit_account_id = generate_debit_account_id()
    print('fund_account_id:', debit_account_id, 'otp:', otp, 'amount:', amount, 'account_id:', account_id) 

    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
    print('user:', user)

    try:
        email_otp = EmailOtp.objects.get(email_otp=otp)
    except EmailOtp.DoesNotExist:
        return Response({'detail': 'OTP does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    if email_otp.is_valid():
        email_otp.delete()

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
    else:
        return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # else:
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
