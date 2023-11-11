# promise/views.py
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

from fund_account.models import (AccountFundBalance,
                    DebitAccountFund,
                    )

from .serializers import PaysofterPromiseSerializer
from .models import PaysofterPromise           

from send_email_otp.serializers import EmailOTPSerializer
from send_email_otp.models import EmailOtp

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model() 


def generate_promise_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'PRO'+''.join(random.choices(letters_and_digits, k=7))


@api_view(['POST'])
@permission_classes([AllowAny])  
def create_promise(request):
    data = request.data
    print("data:", data)

    amount = Decimal(request.data.get('amount'))
    currency = request.data.get('currency')
    duration = request.data.get('duration')
    created_at = request.data.get('created_at')
    public_api_key = request.data.get('public_api_key')
    account_id = data.get('account_id')

    promise_id = generate_promise_id()
    print('promise_id:', promise_id)
    # payment_method = request.data.get('payment_method')
    # payment_provider = request.data.get('payment_provider')
    # card_number = request.data.get('card_number')
    # expiration_month_year = request.data.get('expiration_month_year')
    # cvv = request.data.get('cvv')
    print('account_id:', account_id)

    try:
        seller = User.objects.get(test_api_key=public_api_key)
    except User.DoesNotExist:
        return Response({'detail': 'Seller not found'}, status=status.HTTP_404_NOT_FOUND)
    print('seller:', seller)

    try:
        buyer = User.objects.get(account_id=account_id)
    except User.DoesNotExist:
        return Response({'detail': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)
    print('buyer:', buyer)

    try:      
        promise = PaysofterPromise.objects.create(
            seller=seller,
            buyer=buyer,
            amount=amount,
            currency=currency,
            duration=duration,
            # status=status,
            # is_success=is_success,
            # payer_promise_fulfilled=payer_promise_fulfilled,
            # seller_fulfilled_promise=seller_fulfilled_promise,
            payment_method="Paysofter Promise",
            payment_provider="Paysofter",
            promise_id=promise_id,
        ) 
        promise.save()

        # fund_account_balance, created = AccountFundBalance.objects.get_or_create(user=user)
        # balance = fund_account_balance.balance
        # fund_account_balance.balance += amount 
        # fund_account_balance.save()
        
        # try:
        #     card_data = FundAccountCreditCard.objects.create(
        #         fund_account=fund_account,
        #         card_number=card_number,  
        #         expiration_month_year=expiration_month_year,  
        #         cvv=cvv,  
        #     ) 
        #     print('card_data', card_data)
        # except FundAccountCreditCard.DoesNotExist:
        #     pass

        # send email        
        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)
        sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        sender_email = settings.PAYSOFTER_EMAIL_HOST_USER

        seller_email = seller.email
        seller_first_name = seller.first_name
        seller_account_id = seller.account_id
        formatted_seller_account_id = format_number(seller_account_id)

        buyer_email = buyer.email
        buyer_first_name = buyer.first_name
        buyer_account_id = buyer.account_id
        formatted_buyer_account_id = format_number(buyer_account_id)
        
        print("\nsender_email:", sender_email, "formatted_seller_account_id:", formatted_seller_account_id, "formatted_buyer_account_id:", formatted_buyer_account_id) 
 
        try:
            send_buyer_email(request, sender_name, sender_email, amount, promise_id, created_at, buyer_email, buyer_first_name, formatted_seller_account_id)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            send_seller_email(request, sender_name, sender_email, amount, promise_id, created_at, seller_email, seller_first_name, formatted_buyer_account_id)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'success': f'Promise created successfully.'}, 
                        status=status.HTTP_201_CREATED)
    except PaysofterPromise.DoesNotExist:
            return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_buyer_email(request, sender_name, sender_email, amount, promise_id, created_at, buyer_email, buyer_first_name, formatted_seller_account_id):
    url = settings.PAYSOFTER_URL
    buyer_confirm_promise_link =  f"{url}/buyer-confirm-promise"

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    # subject =  f"[TEST MODE] Notice of Paysofter Promise Alert of NGN {amount} with  Promise ID [{promise_id}]"
    subject =  f"Paysofter Promise Alert"
    buyer_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Promise Alert</title>
            </head>
            <body>
                <p>Hello {buyer_first_name.title()},</p>
                <p>This is to inform you that you have made a promise of <strong>NGN {amount}</strong> with <b>Promise ID: "{promise_id}"</b> to a seller with Account ID: "<strong>{formatted_seller_account_id}</strong>" at <b>{created_at}</b>.</p>
                <p>Click the link below to confirm promise:</p>
                <p><a href="{ buyer_confirm_promise_link }" style="display: inline-block; 
                background-color: #2196f3; color: #fff; padding: 10px 20px; 
                text-decoration: none;">Confirm Promise</a></p>
                <p>If you have any issue with the payment, kindly reply this email.</b></p>
                <p>If you have received this email in error, please ignore it.</p>
                <p>Best regards,</p>
                <p>Paysofter Inc.</p>
            </body>
            </html>
        """ 
    sender = {"name": sender_name, "email": sender_email}
    to = [{"email": buyer_email}]
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


def send_seller_email(request, sender_name, sender_email, amount, promise_id, created_at, seller_email, seller_first_name, formatted_buyer_account_id):
    url = settings.PAYSOFTER_URL
    seller_confirm_promise_link =  f"{url}/seller-confirm-promise"
    
    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    # subject =  f"[TEST MODE] Notice of Paysofter Promise of NGN {amount} with  Promise ID [{promise_id}]"
    subject =  f"Paysofter Promise Alert"
    seller_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Promise Alert</title>
            </head>
            <body>
                <p>Hello {seller_first_name.title()},</p>
                <p>This is to inform you that you have received a promise of <strong>NGN {amount}</strong> with <b>Promise ID: "{promise_id}"</b> from a buyer with Account ID: "<strong>{formatted_buyer_account_id}</strong>" at <b>{created_at}</b>.</p>
                <p>Click the link below to confirm promise:</p>
                <p><a href="{ seller_confirm_promise_link }" style="display: inline-block; 
                background-color: #2196f3; color: #fff; padding: 10px 20px; 
                text-decoration: none;">Confirm Promise</a></p>
                <p>If you have any issue with the payment, kindly reply this email.</b></p>
                <p>If you have received this email in error, please ignore it.</p>
                <p>Best regards,</p>
                <p>Paysofter Inc.</p>
            </body>
            </html>
        """ 
    sender = {"name": sender_name, "email": sender_email}
    to = [{"email": seller_email}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=seller_html_content,
        sender=sender,
        subject=subject
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent!")
    except ApiException as e:
        print(e)
        return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

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


@api_view(['POST'])
@permission_classes([AllowAny])   
def debit_user_fund_account(request):
    user = None  
    data = request.data
    print('data:', data)
    
    account_id = request.data.get('account_id')
    security_code = request.data.get('security_code')
    # amount = request.data.get('amount')
    # amount = int(request.data.get('amount'))
    amount = Decimal(request.data.get('amount'))
    print('account_id', account_id)     

    if account_id:
        try:
            user = User.objects.get(account_id=account_id)
        except User.DoesNotExist:
            return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

    if security_code:
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

    if account_balance.max_withdrawal < amount: 
        return Response({'detail': 'Maximum account fund withrawal exceeded.'}, status=status.HTTP_400_BAD_REQUEST)

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
