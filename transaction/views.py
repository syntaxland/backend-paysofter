# transaction/views.py 
from decimal import Decimal
import random
import string

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException 

from django.conf import settings
from django.contrib.auth import get_user_model 
from .models import Transaction, TransactionCreditCard
from send_email.models import SendBuyerEmail, SendSellerEmail
from .serializers import TransactionSerializer, TransactionCreditCardSerializer
from payment.models import PayoutPayment 

User = get_user_model()


# def generate_transaction_id():
#     return ''.join(random.choices(string.digits, k=10))

# def generate_transaction_id():
#     letters_and_digits = string.ascii_uppercase + string.digits
#     return 'TID'+''.join(random.choices(letters_and_digits, k=14))

def generate_transaction_id():
    return 'TID'+''.join(random.choices(string.digits, k=14))


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_transaction(request): 
    print('Initiateed test transaction...')
 
    amount = Decimal(request.data.get('amount'))
    buyer_email = request.data.get('email')
    created_at = request.data.get('created_at')
    public_api_key = request.data.get('public_api_key')
    currency = request.data.get('currency')

    card_number = request.data.get('card_number')
    # expiration_year = request.data.get('expiration_year')
    expiration_month_year = request.data.get('expiration_month_year') 
    cvv = request.data.get('cvv')
    print('amount:', amount)  
    print('public_api_key:', public_api_key) 
    
    try:
        seller = User.objects.get(test_api_key=public_api_key)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid API key'})
    print('seller:', seller)
    
    transaction_id = generate_transaction_id()

    payment_id = None
    if payment_id == None:
        payment_id = transaction_id
    else:
        payment_id = request.data.get('payment_id')

    try:
        transaction = Transaction.objects.create(
            seller=seller,
            buyer_email=buyer_email,
            amount=amount,  
            currency=currency,  
            payment_method='Debit Card',  
            is_success=True,  
            # is_approved=True,  
            payment_id=payment_id,
            transaction_id=transaction_id,
            payment_provider='Paysofter',  
        ) 

        if transaction.amount > 0:
            transaction.is_approved=True
            transaction.save()
            # transaction.update(is_approved=True)
            
        # print('transaction_data', transaction)

        try:
            card_data = TransactionCreditCard.objects.create(
                transaction=transaction,
                card_number=card_number,  
                # expiration_month=expiration_month,  
                # expiration_year=expiration_year,  
                expiration_month_year=expiration_month_year,  
                cvv=cvv,  
            ) 
            print('card_data', card_data)
        except TransactionCreditCard.DoesNotExist:
            pass

        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)
        # send buyer transaction email        
        # sender_name = "Paysofter Receipt"
        sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
        buyer_email = buyer_email
        seller_email = seller.email
        seller_name = "sellangle.com"
        print("\nbuyer_email:", buyer_email)
        print("seller_email:", seller_email)
        print("\nsender_email:", sender_email)
 
        try:
            send_buyer_email(request, sender_name, sender_email, amount, currency, seller_email, payment_id, seller_name, created_at, buyer_email)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        try:
            send_seller_email(request, sender_name, sender_email, amount, currency, seller_email, payment_id, created_at, buyer_email)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'detail': 'Transaction created successfully'}, status=status.HTTP_201_CREATED)
    except Transaction.DoesNotExist:
        return Response({'detail': 'Payment Transaction not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_buyer_email(request, sender_name, sender_email, amount, currency, seller_email, payment_id, seller_name, created_at, buyer_email):
    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email to buyer...")
    buyer_subject =  f"[TEST MODE] Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
    buyer_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Receipt</title>
            </head>
            <body>
                <p>Dear valued customer,</p>
                <p>You have made a payment of <strong>{amount} {currency}</strong> to <b>{seller_name}</b> with a <b>Payment ID: "{payment_id}"</b> at <b>{created_at}</b>.</p>
                <p>If you have any issue with the payment, kindly reply this email or send email to: <b>{seller_email}</b></p>
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
        subject=buyer_subject
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent!")
    except ApiException as e:
        print(e)
        return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_seller_email(request, sender_name, sender_email, amount, currency, seller_email, payment_id, created_at, buyer_email):
    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    # send seller tranx email
    print("\nSending email to seller...")
    seller_subject =  f"[TEST MODE] Receipt of payment of {amount} {currency} from {buyer_email} with payment ID [{payment_id}]"
    seller_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Receipt</title>
            </head>
            <body>
                <p>Dear valued customer,</p>
                <p>You have received a payment of <strong> {amount} {currency} </strong> from <b>{buyer_email}</b> with a <b>Payment ID: "{payment_id}"</b> at <b>{created_at}</b>.</p>
                <p>This is a mock payment as no real payment is credited to you.</p>
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
        subject=seller_subject
    )
    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent!\n")
    except ApiException as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 
        # return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_transactions(request):
    try:
        user = request.user
        print(user)
        transactions = Transaction.objects.filter(seller=user).order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Transaction.DoesNotExist:
            return Response({'detail': 'Transactions not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def get_all_transactions(request):
    try:
        transactions = Transaction.objects.all().order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Transaction.DoesNotExist:
            return Response({'detail': 'Transactions not found'}, status=status.HTTP_404_NOT_FOUND)
