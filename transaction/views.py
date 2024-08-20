# transaction/views.py
from decimal import Decimal
import random
import string

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Transaction, TransactionCreditCard, TestTransaction
from .serializers import TransactionSerializer, TestTransactionSerializer
from send_email.send_email_sendinblue import send_email_sendinblue

User = get_user_model()


def generate_transaction_id():
    return 'TID'+''.join(random.choices(string.digits, k=17))


@api_view(['POST'])
@permission_classes([AllowAny])
def get_api_key_status(request):
    try:
        public_api_key = request.data.get('public_api_key')
        print('Checking api_key status...:', public_api_key)

        try:
            seller = get_object_or_404(
                User, Q(test_api_key=public_api_key) | Q(live_api_key=public_api_key))
        except User.DoesNotExist:
            return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
        print('seller api_key status:', seller)

        if public_api_key.startswith('test_api_key_'):
            return Response({"api_key_status": "test"}, status=status.HTTP_200_OK)
        elif public_api_key.startswith('live_api_key_'):
            return Response({"api_key_status": "live"}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid API key format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_transaction(request):
    try:
        amount = Decimal(request.data.get('amount'))
        buyer_email = request.data.get('buyer_email')
        buyer_name = request.data.get('buyer_name')
        buyer_phone = request.data.get('buyer_phone')
        created_at = request.data.get('created_at')
        public_api_key = request.data.get('public_api_key')
        currency = request.data.get('currency')
        card_number = request.data.get('card_number')
        expiration_month = request.data.get('expiration_month')
        expiration_year = request.data.get('expiration_year')
        expiration_month_year = request.data.get('expiration_month_year')
        cvv = request.data.get('cvv')
        payment_method = request.data.get('payment_method')
        payment_id = request.data.get('payment_id')
        account_id = request.data.get('account_id')
        print('initiate_transaction public_api_key:', public_api_key)

        transaction_id = generate_transaction_id()
        payment_id = None 

        if payment_id == None:
            payment_id = transaction_id
        else:
            payment_id = request.data.get('payment_id')

        print('transaction_id:', transaction_id)
        print('payment_id:', payment_id)

        try:
            seller = get_object_or_404(
                User, Q(test_api_key=public_api_key) | Q(live_api_key=public_api_key))
        except User.DoesNotExist:
            return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
        print('seller:', seller)

        if public_api_key.startswith('test_'):
            response_data = initiate_test_transaction(request, amount,
                                                      buyer_email,
                                                      buyer_name,
                                                      buyer_phone,
                                                      created_at,
                                                      public_api_key,
                                                      currency,
                                                      card_number,
                                                      expiration_month,
                                                      expiration_year,
                                                      expiration_month_year,
                                                      cvv,
                                                      payment_method,
                                                      account_id,
                                                      payment_id,
                                                      transaction_id,
                                                      seller)
        elif public_api_key.startswith('live_'):
            if not seller.is_api_key_live:
                print('seller.is_api_key_live:', seller.is_api_key_live)
                return Response({'detail': 'API key is currently in test mode. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
            response_data = initiate_live_transaction(request, amount,
                                                    buyer_email,
                                                    buyer_name,
                                                    buyer_phone,
                                                    created_at,
                                                    public_api_key,
                                                    currency,
                                                    card_number,
                                                    expiration_month,
                                                    expiration_year,
                                                    expiration_month_year,
                                                    cvv,
                                                    payment_method,
                                                    account_id,
                                                    payment_id,
                                                    transaction_id,
                                                    seller)
        else:
            return Response({'detail': 'Invalid API key format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(response_data, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def initiate_test_transaction(request, amount, buyer_email, buyer_name, buyer_phone, created_at, public_api_key, currency, card_number, expiration_month, 
                              expiration_year, expiration_month_year, cvv, payment_method, account_id, payment_id, transaction_id, seller):
    print('Initiated test transaction...',created_at)

    # try:
    #     seller = User.objects.get(test_api_key=public_api_key)
    # except User.DoesNotExist:
    #     return {'detail': 'Invalid API key. Please contact the seller.', 'status': 404}
    # print('seller:', seller)

    try:
        transaction = TestTransaction.objects.create(
            seller=seller,
            buyer_email=buyer_email,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            is_success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            payment_provider='Paysofter',
        )

        if transaction.amount > 0:
            transaction.is_approved = True
            transaction.save()

        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)

        buyer_email = buyer_email
        seller_email = seller.email
        formatted_buyer_card_no = format_number(card_number)
        formatted_buyer_account_id = format_number(account_id)

        if payment_method == "Debit Card":
            try:
                send_test_buyer_card_transaction_email(
                    request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
            try:
                send_test_seller_card_transaction_email(
                    request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
        elif payment_method == "Paysofter Account Fund":
            try:
                send_test_buyer_fund_transaction_email(
                    request, amount, currency, seller_email, payment_id, buyer_email, formatted_buyer_account_id, created_at)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
            try:
                send_test_seller_fund_transaction_email(
                    request, amount, currency, seller_email, payment_id, buyer_email, formatted_buyer_account_id, created_at)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
        else:
            return {'detail': 'Invalid payment method. Please contact the seller.', 'status': 400}

        return {'detail': 'Transaction created successfully', 'status': 201}
    except Transaction.DoesNotExist:
        return {'detail': 'Payment Transaction not found', 'status': 404}
    except Exception as e:
        return {'detail': str(e), 'status': 500}


def send_test_buyer_card_transaction_email(request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no):
    print("Sending transaction email...", created_at)
    try:
        subject = f"[TEST MODE] Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have made a payment of <strong>{amount} {currency}</strong> to <b>{seller_email}</b> 
                            with a <b>Payment ID: "{payment_id}"</b> and card number ending in <strong>{formatted_buyer_card_no}</strong>
                              at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Card No.</td>
                                    <td>{formatted_buyer_card_no}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p>Note: This is a mock promise transaction as no real money is debited or credited.</p>
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_test_seller_card_transaction_email(request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no):
    print("Sending transaction email...", created_at)
    try:
        subject = f"[TEST MODE] Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have received a payment of <strong> {amount} {currency} </strong> from <b>{buyer_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and card number ending in <strong>{formatted_buyer_card_no}</strong> 
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Email</td>
                                    <td>{buyer_email}</td>
                                </tr>
                                <tr>
                                    <td>Card No.</td>
                                    <td>{formatted_buyer_card_no}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p>Note: This is a mock promise transaction as no real money is debited or credited.</p>
                            <p><em>If you have any issue with this payment, kindly reply this email.</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_test_buyer_fund_transaction_email(request, amount, currency, seller_email, payment_id,
                                           buyer_email, formatted_buyer_account_id, created_at):
    print("Sending transaction email...", created_at)
    try:
        subject = f"[TEST MODE] Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have made a payment of <strong> {amount} {currency} </strong> to <b>{seller_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and Paysofter Account Fund with Account ID ending in:
                                      ({formatted_buyer_account_id})
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Paysofter Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p>Note: This is a mock promise transaction as no real money is debited or credited.</p>
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_test_seller_fund_transaction_email(request, amount, currency, seller_email, payment_id,
                                            buyer_email, formatted_buyer_account_id, created_at):
    print("Sending transaction email...", created_at)
    try:
        subject = f"[TEST MODE] Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have received a payment of <strong> {amount} {currency} </strong> from <b>{buyer_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and Paysofter Account Fund with Account ID ending in: ({formatted_buyer_account_id})
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Email</td>
                                    <td>{buyer_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Paysofter Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p>Note: This is a mock promise transaction as no real money is debited or credited.</p>
                            <p><em>If you have any issue with this payment, kindly reply this email.</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def initiate_live_transaction(request, amount,
                              buyer_email,
                              buyer_name, 
                              buyer_phone, 
                              created_at,
                              public_api_key,
                              currency,
                              card_number,
                              expiration_month,
                              expiration_year,
                              expiration_month_year,
                              cvv,
                              payment_method,
                              account_id,
                              payment_id,
                              transaction_id,
                              seller):
    print('Initiated live transaction...',created_at)

    # try:
    #     seller = User.objects.get(live_api_key=public_api_key)
    # except User.DoesNotExist:
    #     return {'detail': 'Invalid API key. Please contact the seller.', 'status': 404}
    # print('seller:', seller)

    try:
        transaction = Transaction.objects.create(
            seller=seller,
            buyer_email=buyer_email,
            buyer_name=buyer_name,
            buyer_phone=buyer_phone,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            is_success=True,
            payment_id=payment_id,
            transaction_id=transaction_id,
            payment_provider='Paysofter',
        )

        if transaction.amount > 0:
            transaction.is_approved = True
            transaction.save()
            # transaction.update(is_approved=True)
        try:
            card_data = TransactionCreditCard.objects.create(
                transaction=transaction,
                card_number=card_number,
                expiration_month=expiration_month,
                expiration_year=expiration_year,
                expiration_month_year=expiration_month_year,
                cvv=cvv,
            )
            print('card_data', card_data)
        except TransactionCreditCard.DoesNotExist:
            pass

        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        print("\amount:", amount)
        # send buyer transaction email
        buyer_email = buyer_email
        seller_email = seller.email
        # seller_name = "sellangle.com"
        formatted_buyer_card_no = format_number(card_number)
        formatted_buyer_account_id = format_number(account_id)
        # print("\nbuyer_email:", buyer_email)

        if payment_method == "Debit Card":
            try:
                send_buyer_card_transaction_email(
                    request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
            try:
                send_seller_card_transaction_email(
                    request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
        elif payment_method == "Paysofter Account Fund":
            try:
                send_buyer_fund_transaction_email(
                    request, amount, currency, seller_email, payment_id, buyer_email, formatted_buyer_account_id, created_at)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
            try:
                send_seller_fund_transaction_email(
                    request, amount, currency, seller_email, payment_id, buyer_email, formatted_buyer_account_id, created_at)
            except Exception as e:
                print(e)
                return {'detail': str(e), 'status': 500}
        else:
            return {'detail': 'Invalid payment method. Please contact the seller.', 'status': 400}
        return {'detail': 'Transaction created successfully', 'status': 201}
    
    except Transaction.DoesNotExist:
        return {'detail': 'Payment Transaction not found', 'status': 404}
    except Exception as e:
        return {'detail': str(e), 'status': 500}


def send_buyer_card_transaction_email(request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no):
    print("Sending transaction email...", created_at)
    try:
        subject = f"Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have made a payment of <strong>{amount} {currency}</strong> to <b>{seller_email}</b> 
                            with a <b>Payment ID: "{payment_id}"</b> and card number ending in <strong>{formatted_buyer_card_no}</strong>
                              at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Card No.</td>
                                    <td>{formatted_buyer_card_no}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_seller_card_transaction_email(request, amount, currency, seller_email, payment_id, created_at, buyer_email, formatted_buyer_card_no):
    print("Sending transaction email...", created_at)
    try:
        subject = f"Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have received a payment of <strong> {amount} {currency} </strong> from <b>{buyer_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and card number ending in <strong>{formatted_buyer_card_no}</strong> 
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Email</td>
                                    <td>{buyer_email}</td>
                                </tr>
                                <tr>
                                    <td>Card No.</td>
                                    <td>{formatted_buyer_card_no}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p><em>If you have any issue with this payment, kindly reply this email.</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_buyer_fund_transaction_email(request, amount, currency, seller_email, payment_id,
                                      buyer_email, formatted_buyer_account_id, created_at):
    print("Sending transaction email...", created_at)
    try:
        subject = f"Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have made a payment of <strong> {amount} {currency} </strong> to <b>{seller_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and Paysofter Account Fund with Account ID ending in:
                                      ({formatted_buyer_account_id})
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Paysofter Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


def send_seller_fund_transaction_email(request, amount, currency, seller_email, payment_id,
                                       buyer_email, formatted_buyer_account_id, created_at):
    print("Sending transaction email...", created_at)
    try:
        subject = f"Receipt of payment of {amount} {currency} to {seller_email} with payment ID [{payment_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Receipt</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Receipt</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>You have received a payment of <strong> {amount} {currency} </strong> from <b>{buyer_email}</b> 
                                with a <b>Payment ID: "{payment_id}"</b> and Paysofter Account Fund with Account ID ending in: ({formatted_buyer_account_id})
                                at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Payment ID</td>
                                    <td>{payment_id}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Email</td>
                                    <td>{buyer_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Paysofter Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p><em>If you have any issue with this payment, kindly reply this email.</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_transactions(request):
    try:
        user = request.user
        print(user)
        transactions = Transaction.objects.filter(
            seller=user).order_by('-timestamp')
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except Transaction.DoesNotExist:
        return Response({'detail': 'Transactions not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_test_transactions(request):
    try:
        user = request.user
        print(user)
        transactions = TestTransaction.objects.filter(
            seller=user).order_by('-timestamp')
        serializer = TestTransactionSerializer(transactions, many=True)
        return Response(serializer.data)
    except TestTransaction.DoesNotExist:
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
