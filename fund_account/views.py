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

from .models import (FundAccount, 
                     AccountFundBalance,
                    DebitAccountFund,
                    FundAccountCreditCard,
                    UsdAccountFundBalance,
                    FundUsdAccount,
                    DebitUsdAccountFund,
                    UsdFundAccountCreditCard
                    )

from .serializers import (FundAccountSerializer, 
                          AccountFundBalanceSerializer, 
                          DebitAccountFundSerializer, 
                          OtpDataSerializer,
                          UsdAccountFundBalanceSerializer,
                            FundUsdAccountSerializer,
                            DebitUsdAccountFundFundSerializer
                          )

# from send_email_otp.serializers import EmailOTPSerializer
from send_email_otp.models import EmailOtp

from django.db.models import Q
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
    data = request.data
    print("data:", data, "user:", user)

    amount = Decimal(request.data.get('amount'))
    currency = request.data.get('currency')
    # payment_method = request.data.get('payment_method')
    # payment_provider = request.data.get('payment_provider')
    created_at = request.data.get('created_at')

    fund_account_id = generate_fund_account_id()
    print('fund_account_id:', fund_account_id)

    card_number = request.data.get('card_number')
    expiration_month_year = request.data.get('expiration_month_year')
    cvv = request.data.get('cvv')
    print('amount:', amount)

    try:  
        fund_account_balance, created = AccountFundBalance.objects.get_or_create(user=user)
        old_bal = fund_account_balance.balance    

        fund_account = FundAccount.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            old_bal=old_bal,
            payment_method="Debit Card",
            payment_provider="Mastercard",
            fund_account_id=fund_account_id,
        ) 
        
        fund_account_balance.balance += amount 
        fund_account_balance.save()

        fund_account.is_success = True
        fund_account.new_bal = fund_account_balance.balance    
        fund_account.save()
        
        try:
            card_data = FundAccountCreditCard.objects.create(
                fund_account=fund_account,
                card_number=card_number,  
                expiration_month_year=expiration_month_year,  
                cvv=cvv,  
            ) 
            print('card_data', card_data)
        except FundAccountCreditCard.DoesNotExist:
            pass

        # send email        
        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)
        sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
        user_email = user.email
        first_name = user.first_name
        
        print("\nsender_email:", sender_email, "user_email:", user_email) 
 
        try:
            send_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': f'Fund account request submitted successfully. Old Bal: NGN {old_bal}'}, 
                        status=status.HTTP_201_CREATED)
    except FundAccount.DoesNotExist:
            return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name):
    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    subject =  f"[TEST MODE] Notice of Paysofter account fund of {amount} {currency} with  Account Fund ID [{fund_account_id}]"
    buyer_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Receipt</title>
            </head>
            <body>
                <p>Dear {first_name},</p>
                <p>You have funded your Paysofter account with <strong>{amount} {currency}</strong> with  <b>Account Fund ID: "{fund_account_id}"</b> at <b>{created_at}</b>.</p>
                <p>If you have any issue with the payment, kindly reply this email.</b></p>
                <p>If you have received this email in error, please ignore it.</p>
                <p>Best regards,</p>
                <p>Paysofter Inc.</p>
            </body>
            </html>
        """ 
    sender = {"name": sender_name, "email": sender_email}
    to = [{"email": user_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=buyer_html_content,
        sender=sender,
        subject=subject
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent!")
    except ApiException as e:
        print(e)
        return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# def format_email(email):
#     if '@' in email:
#         parts = email.split('@')
#         if len(parts[0]) < 2 or len(parts[1]) < 2:
#             # If the username or domain is too short, don't modify the email
#             return email
#         else:
#             username = parts[0][0] + '*' * (len(parts[0]) - 2) + parts[0][-1]
#             domain = parts[1][0] + '*' * (len(parts[1]) - 2) + parts[1][-1]
#             return f"{username}@{domain}"
#     else:
#         # If there's no '@' character in the email, don't modify it
#         return email


# def format_number(number):
#     number_str = str(number)

#     if len(number_str) < 4:
#         # If the number is too short, don't modify it
#         return number_str
#     else:
#         masked_part = '*' * (len(number_str) - 4) + number_str[-4:]
#         return masked_part


@api_view(['POST'])
@permission_classes([AllowAny])   
def debit_user_fund_account(request):
    # user = None  
    data = request.data
    print('data:', data)
    
    account_id = request.data.get('account_id')
    security_code = request.data.get('security_code')
    # amount = request.data.get('amount')
    # amount = int(request.data.get('amount'))
    amount = Decimal(request.data.get('amount'))
    print('account_id', account_id)     
    public_api_key = request.data.get('public_api_key')
    print('public_api_key:', public_api_key)

    # if account_id:
    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

    # if security_code:
    try:
        user = User.objects.get(security_code=security_code)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or expired Security Code.'}, status=status.HTTP_404_NOT_FOUND)
    
    if user is None:
        return Response({'detail': 'Invalid Account ID or Security Code is expired.'}, status=status.HTTP_404_NOT_FOUND)
    
    print('user:', user)

    try:
        account_balance = AccountFundBalance.objects.get(user=user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found'}, status=status.HTTP_400_BAD_REQUEST)

    if account_balance.is_diabled == True: 
        return Response({'detail': 'Account fund is currently diabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

    if account_balance.is_active == False: 
        return Response({'detail': 'Account fund is currently inactive.'}, status=status.HTTP_400_BAD_REQUEST)

    if account_balance.max_withdrawal is None: 
        return Response({'detail': 'Maximum account fund value is set to None. Please set a minimum value for the Account Fund.'}, status=status.HTTP_400_BAD_REQUEST)

    if account_balance.max_withdrawal < amount: 
        return Response({'detail': 'Maximum account fund withrawal exceeded.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        seller_api_key = User.objects.get(test_api_key=public_api_key)
        # if not seller_api_key:
        #     return Response({'detail': 'Seller API Key found'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or Seller API Key not found'}, status=status.HTTP_401_UNAUTHORIZED)
    print('seller_api_key:', seller_api_key)

    payer_email = user.email
    first_name = user.first_name
    formatted_payer_email = format_email(payer_email)
    print('payer_email:', payer_email, 'first_name:', first_name, 'formatted_payer_email:', formatted_payer_email)
    
    # Send email
    try:
        send_payer_account_fund_otp(request, payer_email, first_name)
    except Exception as e:
        print(e)
        # return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'detail': 'Email sent.', '275887': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)
    

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
    amount = Decimal(otp_data.get('amount'))
    account_id = otp_data.get('account_id')
    currency = otp_data.get('currency')
    debit_account_id = generate_debit_account_id()
    print('fund_account_id:', debit_account_id, 'otp:', otp, 'amount:', amount, 'account_id:', account_id) 

    # public_api_key = request.data.get('public_api_key')
    # try:
    #     seller_api_key = User.objects.get(test_api_key=public_api_key)
    #     if seller_api_key:
    #         return Response({'detail': 'Seller API Key found'}, status=status.HTTP_200_OK)
    # except User.DoesNotExist:
    #     return Response({'detail': 'Invalid or Seller API Key not found'}, status=status.HTTP_401_UNAUTHORIZED)
    # print('seller_api_key:', seller_api_key)

    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
    print('user:', user)

    try:
        email_otp = EmailOtp.objects.get(email_otp=otp)
    except EmailOtp.DoesNotExist:
        return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_404_NOT_FOUND)
    
    if email_otp.is_valid():
        email_otp.delete()

        try:
            account_balance, created = AccountFundBalance.objects.get_or_create(user=user)
            
            # balance = account_balance.balance
            old_bal = account_balance.balance    
            print('old balance:', old_bal)

            if old_bal < amount: 
                return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
            account_balance.balance -= amount 
            account_balance.save()
            print('new balance:', account_balance.balance)

            debit_fund_account = DebitAccountFund.objects.create(
                user=user,
                amount=amount,
                currency=currency,
                old_bal=old_bal,
                # payment_method=payment_method,
                # payment_provider=payment_provider,
                debit_account_id=debit_account_id,
            ) 
            debit_fund_account.is_success = True
            debit_fund_account.new_bal = account_balance.balance    
            debit_fund_account.save()
            return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
        except DebitAccountFund.DoesNotExist:
            return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)                                  
    else:
        return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_debits(request):
    user = request.user
    try:
        account_debits = DebitAccountFund.objects.filter(user=user).order_by('-timestamp')
        serializer = DebitAccountFundSerializer(account_debits, many=True)
        return Response(serializer.data)
    except DebitAccountFund.DoesNotExist:
        return Response({'detail': 'Debit account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_account_fund_balance(request):
    try:
        account_fund_balance, created = AccountFundBalance.objects.get_or_create(user=request.user)
        serializer = AccountFundBalanceSerializer(account_fund_balance)
        return Response(serializer.data)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Fund account balance not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def get_all_account_fund_balance(request):
    try:
        account_fund_balance = AccountFundBalance.objects.filter().order_by('-timestamp')
        serializer = AccountFundBalanceSerializer(account_fund_balance, many=True)
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


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_account_funds_debits(request):
    user = request.user
    try:
        account_funds = DebitAccountFund.objects.filter(user=user).order_by('-timestamp')
        serializer = DebitAccountFundSerializer(account_funds, many=True)
        return Response(serializer.data)
    except DebitAccountFund.DoesNotExist:
        return Response({'detail': 'Fund account debits not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_account_funds_credits(request):
    user = request.user
    try:
        account_funds = FundAccount.objects.filter(user=user).order_by('-timestamp')
        serializer = FundAccountSerializer(account_funds, many=True)
        return Response(serializer.data)
    except FundAccount.DoesNotExist:
        return Response({'detail': 'Fund account credits not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_is_account_active(request):
    user = request.user
    data = request.data
    password = data.get('password')

    # Check if the provided password is correct for the user
    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account_balance = AccountFundBalance.objects.get(user=user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    if account_balance.is_diabled == True: 
        return Response({'detail': 'Account fund is currently disabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
    account_balance.is_active = not account_balance.is_active
    account_balance.save()

    print(f'Account fund status toggled to {account_balance.is_active}.')
    return Response({'detail': f'USD Account Fund status toggled to {account_balance.is_active}.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_maximum_fund_withdrawal(request):
    user = request.user
    data = request.data
    print('data:', data, 'user:', user)

    amount = Decimal(request.data.get('amount'))
    print('amount:', amount) 

    try:
        account_balance = AccountFundBalance.objects.get(user=user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found'}, status=status.HTTP_404_NOT_FOUND)
    
    print('account_balance:', account_balance.balance)
    print('max_withdrawal(before):', account_balance.max_withdrawal)

    try:
        account_balance.max_withdrawal = amount
        account_balance.save()
        print('max_withdrawal(after):', account_balance.max_withdrawal)
        return Response({'detail': f'Maximum fund withrawal of {amount} set.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_maximum_usd_fund_withdrawal(request):
    user = request.user
    data = request.data
    print('data:', data, 'user:', user)

    amount = Decimal(request.data.get('amount'))
    print('amount:', amount) 

    try:
        account_balance = UsdAccountFundBalance.objects.get(user=user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found'}, status=status.HTTP_404_NOT_FOUND)
    
    print('account_balance:', account_balance.balance)
    print('max_withdrawal(before):', account_balance.max_withdrawal)

    try:
        account_balance.max_withdrawal = amount
        account_balance.save()
        print('max_withdrawal(after):', account_balance.max_withdrawal)
        return Response({'detail': f'Maximum fund withrawal of {amount} set.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([AllowAny])
def send_otp_account_fund_disable(request):
    data = request.data
    print('data:', data)

    email = data.get('identifier')
    account_id = data.get('identifier')
    print('email:', email, 'account_id:', account_id)

    try:
        user = User.objects.get(
                Q(email=email) |
                Q(account_id=account_id)
        )
    except User.DoesNotExist:
        return Response({'detail': 'Invalid email or Account ID.'}, status=status.HTTP_404_NOT_FOUND)
    
    email = user.email
    formatted_email = format_email(email)
    first_name = user.first_name
    print('formatted_email:', formatted_email, 'first_name:', first_name)

    try:
        send_deactivate_account_fund_otp(request, email, first_name)
    except Exception as e:
        print(e)
        return Response({'error': 'Error sending email. Please check your network connection.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'detail': f'Email {email} sent.', 'formattedEmail': formatted_email}, status=status.HTTP_200_OK) 


def send_deactivate_account_fund_otp(request, email, first_name):
    print('first_name:', first_name, 'payer_email:',  email)

    email_otp, created = EmailOtp.objects.get_or_create(email=email)
    email_otp.generate_email_otp()
    print('email_otp:', email_otp, "email_otp:", email_otp.email_otp)

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
    # Sending email
    subject = "Disable Account Fund OTP"
    print("\nSending email OTP...")
    html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Disable Account Fund OTP</title>
        </head>
        <body>
            <p>Dear {first_name.title()},</p>
            <p>To disable your Paysofter Account Fund, please use the OTP provided below:</p>
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
    to = [{"email": email, "name": first_name}]
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
def verify_otp_account_fund_disable(request):
    data = request.data

    otp = data.get('otp')
    email = data.get('identifier')
    account_id = data.get('identifier')

    try:
        email_otp = EmailOtp.objects.get(email_otp=otp)
    except EmailOtp.DoesNotExist:
        return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_404_NOT_FOUND)
    
    if email_otp.is_valid():
        email_otp.delete()

    try:
        user = User.objects.get(
                Q(email=email) |
                Q(account_id=account_id)
        )
    except User.DoesNotExist:
        return Response({'detail': 'Invalid email or Account ID'}, status=status.HTTP_404_NOT_FOUND)
    
    email = user.email
    formatted_email = format_email(email)

    first_name = user.first_name
    print('formatted_email:', formatted_email, 'first_name:', first_name)

    try:
        account_balance = AccountFundBalance.objects.get(user=user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    if account_balance.is_diabled == True: 
        return Response({'detail': 'Account fund is already disabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
    account_balance.is_diabled = True
    account_balance.save() 

    try:
        usd_account_balance = UsdAccountFundBalance.objects.get(user=user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'USD Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    if usd_account_balance.is_diabled == True: 
        return Response({'detail': 'Account fund is already disabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
    usd_account_balance.is_diabled = True
    usd_account_balance.save() 

    print(f'Account fund deactivated.')
    return Response({'detail': f'Account fund deactivated.', 'formattedEmail': formatted_email}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def activate_account_fund(request):
    data = request.data
    user = request.user
    print('data:', data)

    account_id = data.get('account_id')
    password = data.get('password')

    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        account_fund_user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid email or Account ID'}, status=status.HTTP_404_NOT_FOUND)

    try:
        account_balance = AccountFundBalance.objects.get(user=account_fund_user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    account_balance.is_diabled = False
    account_balance.is_active = False
    account_balance.save() 

    print(f'Account fund deactivated.')
    return Response({'detail': f'Account fund activated.',}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])  
def fund_user_usd_account(request):
    user = request.user
    data = request.data
    print("data:", data)

    amount = Decimal(request.data.get('amount'))
    currency = request.data.get('currency')
    # payment_method = request.data.get('payment_method')
    # payment_provider = request.data.get('payment_provider')
    created_at = request.data.get('created_at')

    fund_account_id = generate_fund_account_id()
    print('fund_account_id:', fund_account_id)

    card_number = request.data.get('card_number')
    expiration_month_year = request.data.get('expiration_month_year')
    cvv = request.data.get('cvv')
    print('amount:', amount)
    
    try:      
        fund_account_balance, created = UsdAccountFundBalance.objects.get_or_create(user=user)
        old_bal = fund_account_balance.balance    
        fund_account_balance.balance += amount 
        fund_account_balance.save()

        fund_account = FundUsdAccount.objects.create(
            user=user,
            amount=amount,
            currency=currency,
            old_bal=old_bal,
            payment_method="Debit Card",
            payment_provider="Mastercard",
            fund_account_id=fund_account_id,
        ) 
        fund_account.is_success = True
        fund_account.new_bal = fund_account_balance.balance    
        fund_account.save()       
        
        try:
            card_data = UsdFundAccountCreditCard.objects.create(
                fund_account=fund_account,
                card_number=card_number,  
                expiration_month_year=expiration_month_year,  
                cvv=cvv,  
            ) 
            print('card_data', card_data)
        except UsdFundAccountCreditCard.DoesNotExist:
            pass

        # send email        
        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)
        sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
        user_email = user.email
        first_name = user.first_name
        
        print("\nsender_email:", sender_email, "user_email:", user_email) 
 
        try:
            send_usd_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': f'Fund account request submitted successfully. Old Bal: NGN {old_bal}'}, 
                        status=status.HTTP_201_CREATED)
    except FundUsdAccount.DoesNotExist:
            return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_usd_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name):
    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    subject =  f"[TEST MODE] Notice of Paysofter account fund of {amount} {currency} with  Account Fund ID [{fund_account_id}]"
    buyer_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Receipt</title>
            </head>
            <body>
                <p>Dear {first_name},</p>
                <p>You have funded your Paysofter account with <strong>{amount} {currency}</strong> with  <b>Account Fund ID: "{fund_account_id}"</b> at <b>{created_at}</b>.</p>
                <p>If you have any issue with the payment, kindly reply this email.</b></p>
                <p>If you have received this email in error, please ignore it.</p>
                <p>Best regards,</p>
                <p>Paysofter Inc.</p>
            </body>
            </html>
        """ 
    sender = {"name": sender_name, "email": sender_email}
    to = [{"email": user_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=buyer_html_content,
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
def debit_user_usd_account_fund(request):
    data = request.data
    print('data:', data)
    
    account_id = request.data.get('account_id')
    security_code = request.data.get('security_code')
    amount = Decimal(request.data.get('amount'))
    print('account_id', account_id)     
    public_api_key = request.data.get('public_api_key')
    print('public_api_key:', public_api_key)

    try:
        user = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

    try:
        user = User.objects.get(security_code=security_code)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or expired Security Code.'}, status=status.HTTP_404_NOT_FOUND)
    
    if user is None:
        return Response({'detail': 'Invalid Account ID or Security Code is expired.'}, status=status.HTTP_404_NOT_FOUND)
    
    print('user:', user)

    try:
        usd_account_balance = UsdAccountFundBalance.objects.get(user=user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found'}, status=status.HTTP_400_BAD_REQUEST)

    if usd_account_balance.is_diabled == True: 
        return Response({'detail': 'Account fund is currently diabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

    if usd_account_balance.is_active == False: 
        return Response({'detail': 'Account fund is currently inactive.'}, status=status.HTTP_400_BAD_REQUEST)

    if usd_account_balance.max_withdrawal is None: 
        return Response({'detail': 'Maximum account fund value is set to None. Please set a minimum value for the Account Fund.'}, status=status.HTTP_400_BAD_REQUEST)

    if usd_account_balance.max_withdrawal < amount: 
        return Response({'detail': 'Maximum account fund withrawal exceeded.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        seller_api_key = User.objects.get(test_api_key=public_api_key)
        # if not seller_api_key:
        #     return Response({'detail': 'Seller API Key found'}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or Seller API Key not found'}, status=status.HTTP_401_UNAUTHORIZED)
    print('seller_api_key:', seller_api_key)

    payer_email = user.email
    first_name = user.first_name
    formatted_payer_email = format_email(payer_email)
    print('payer_email:', payer_email, 'first_name:', first_name, 'formatted_payer_email:', formatted_payer_email)
    
    # Send email
    try:
        send_usd_payer_account_fund_otp(request, payer_email, first_name)
    except Exception as e:
        print(e)
        # return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response({'detail': 'Email sent.', '275887': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)
    

def send_usd_payer_account_fund_otp(request, payer_email, first_name):
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
def verify_usd_account_debit_email_otp(request):
    data = request.data
    print('data:', data)
 
    otp_data = request.data.get('otpData', {}) 
    otp = otp_data.get('otp')
    amount = Decimal(otp_data.get('amount'))
    account_id = otp_data.get('account_id')
    currency = otp_data.get('currency')
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
        return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_404_NOT_FOUND)
    
    if email_otp.is_valid():
        email_otp.delete()

        try:
            account_balance, created = UsdAccountFundBalance.objects.get_or_create(user=user)
            
            old_bal = account_balance.balance
            # old_bal = account_balance.balance    
            print('old balance:', old_bal)

            if old_bal < amount: 
                return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
            account_balance.balance -= amount 
            account_balance.save()
            print('new balance:', account_balance.balance)

            debit_fund_account = DebitUsdAccountFund.objects.create(
                user=user,
                amount=amount,
                currency=currency,
                                old_bal=old_bal,
                # payment_method=payment_method,
                # payment_provider=payment_provider,
                debit_account_id=debit_account_id,
            ) 
            debit_fund_account.is_success = True
            debit_fund_account.new_bal = account_balance.balance    
            debit_fund_account.save()
            return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
        except DebitUsdAccountFund.DoesNotExist:
            return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)                                  
    else:
        return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_usd_account_fund_balance(request):
    try:
        account_fund_balance, created = UsdAccountFundBalance.objects.get_or_create(user=request.user)
        serializer = UsdAccountFundBalanceSerializer(account_fund_balance)
        return Response(serializer.data)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'USD fund account balance not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def get_user_usd_account_fund_credits(request):
    user = request.user
    try:
        account_funds = FundUsdAccount.objects.filter(user=user).order_by('-timestamp') 
        serializer = FundUsdAccountSerializer(account_funds, many=True)
        return Response(serializer.data)
    except FundUsdAccount.DoesNotExist:
        return Response({'detail': 'USD account funds not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_usd_account_debits(request):
    user = request.user
    try:
        account_debits = DebitUsdAccountFund.objects.filter(user=user).order_by('-timestamp')
        serializer = DebitUsdAccountFundFundSerializer(account_debits, many=True)
        return Response(serializer.data)
    except DebitUsdAccountFund.DoesNotExist:
        return Response({'detail': 'Debit account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_usd_maximum_fund_withdrawal(request):
    user = request.user
    data = request.data
    print('data:', data, 'user:', user)

    amount = Decimal(request.data.get('amount'))
    print('amount:', amount) 

    try:
        account_balance = UsdAccountFundBalance.objects.get(user=user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found'}, status=status.HTTP_404_NOT_FOUND)
    
    print('account_balance:', account_balance.balance)
    print('max_withdrawal(before):', account_balance.max_withdrawal)

    try:
        account_balance.max_withdrawal = amount
        account_balance.save()
        print('max_withdrawal(after):', account_balance.max_withdrawal)
        return Response({'detail': f'Maximum fund withrawal of {amount} set.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_is_usd_account_active(request):
    user = request.user
    data = request.data
    password = data.get('password')

    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        usd_account_balance = UsdAccountFundBalance.objects.get(user=user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'USD Account Fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    if usd_account_balance.is_diabled == True: 
        return Response({'detail': 'USD Account Fund is currently disabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)
    usd_account_balance.is_active = not usd_account_balance.is_active
    usd_account_balance.save()

    return Response({'detail': f'USD Account Fund status toggled.'}, status=status.HTTP_200_OK)



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


def format_number(number):
    number_str = str(number)

    if len(number_str) < 4:
        # If the number is too short, don't modify it
        return number_str
    else:
        masked_part = '*' * (len(number_str) - 4) + number_str[-4:]
        return masked_part
