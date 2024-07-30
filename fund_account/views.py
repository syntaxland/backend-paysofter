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
                     UsdFundAccountCreditCard,
                     TestDebitAccountFund
                     )

from .serializers import (FundAccountSerializer,
                          AccountFundBalanceSerializer,
                          DebitAccountFundSerializer,
                          OtpDataSerializer,
                          UsdAccountFundBalanceSerializer,
                          FundUsdAccountSerializer,
                          DebitUsdAccountFundFundSerializer
                          )

from send_email.send_email_sendinblue import send_email_sendinblue
from send_email_otp.models import EmailOtp

from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_fund_account_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'AFD'+''.join(random.choices(letters_and_digits, k=17))


def generate_debit_account_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'DBF'+''.join(random.choices(letters_and_digits, k=17))


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def fund_user_account_view(request):
    user = request.user
    data = request.data
    print("data:", data, "user:", user)

    amount = Decimal(request.data.get('amount'))
    currency = request.data.get('currency')
    # payment_method = request.data.get('payment_method')
    created_at = request.data.get('created_at')

    fund_account_id = generate_fund_account_id()
    print('fund_account_id:', fund_account_id)

    card_number = request.data.get('card_number')
    expiration_month = request.data.get('expiration_month')
    expiration_year = request.data.get('expiration_year')
    expiration_month_year = request.data.get('expiration_month_year')
    cvv = request.data.get('cvv')
    print('amount:', amount)

    try:
        fund_account_balance, created = AccountFundBalance.objects.get_or_create(
            user=user)
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
                expiration_month=expiration_month,
                expiration_year=expiration_year,
                expiration_month_year=expiration_month_year,
                cvv=cvv,
            )
            print('card_data', card_data)
        except FundAccountCreditCard.DoesNotExist:
            pass

        new_bal = fund_account_balance.balance

        # send email
        amount = '{:,.0f}'.format(float(amount))
        print("\amount:", amount)
        old_bal = '{:,.0f}'.format(old_bal)
        new_bal = '{:,.0f}'.format(new_bal)
        user_email = user.email
        first_name = user.first_name

        try:
            send_fund_credit_alert_email(request, amount, currency, fund_account_id, created_at, user_email, first_name, old_bal, new_bal)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': f'Fund account request submitted successfully. Old Bal: NGN {old_bal}'},
                        status=status.HTTP_201_CREATED)
    except FundAccount.DoesNotExist:
        return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def send_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name):
#     # Email Sending API Config
#     configuration = sib_api_v3_sdk.Configuration()
#     configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
#     api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
#         sib_api_v3_sdk.ApiClient(configuration))

#     # Sending email
#     print("\nSending email...")
#     subject = f"[TEST MODE] Notice of Paysofter account fund of {amount} {currency} with  Account Fund ID [{fund_account_id}]"
#     html_content = f"""
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <title>Paysofter Receipt</title>
#             </head>
#             <body>
#                 <p>Dear {first_name},</p>
#                 <p>You have funded your Paysofter account with <strong>{amount} {currency}</strong> with  <b>Account Fund ID: 
#                 "{fund_account_id}"</b> at <b>{created_at}</b>.</p>
#                 <p>If you have any issue with the payment, kindly reply this email.</b></p>
#                 <p>If you have received this email in error, please ignore it.</p>
#                 <p>Best regards,</p>
#                 <p>Paysofter Inc.</p>
#             </body>
#             </html>
#         """
#     sender = {"name": sender_name, "email": sender_email}
#     to = [{"email": user_email}]
#     send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#         to=to,
#         html_content=html_content,
#         sender=sender,
#         subject=subject
#     )
#     try:
#         api_response = api_instance.send_transac_email(send_smtp_email)
#         print("Email sent!")
#     except ApiException as e:
#         print(e)
#         return {'detail': str(e), 'status': 500}


def send_fund_credit_alert_email(request, amount, currency, fund_account_id, created_at, user_email, first_name, old_bal, new_bal):
    print("Sending Credit alert email...")
    try:
        subject = f"Paysofter Account Fund Credit Alert of {amount} {currency} with Credit Fund ID [{fund_account_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Account Fund Credit Alert</title>
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
                            background-color: green;
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
                            <h2>Paysofter Account Fund Debit Alert</h2>
                        </div>
                        <div class="content">
                            <p>Dear {first_name},</p>
                            <p>You have funded your Paysofter account with <strong>{amount} {currency}</strong> with  <b>Account Fund ID: 
                            "{fund_account_id}"</b> at <b>{created_at}</b>.</p>
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
                                    <td>Transaction ID</td>
                                    <td>{fund_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Old Bal</td>
                                    <td>{old_bal}  {currency}</td>
                                </tr>
                                <tr>
                                    <td>New Bal</td>
                                    <td>{new_bal}  {currency}</td>
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
                            <p><em>If you have any issue with this payment, kindly reply this email.</em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": user_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


@api_view(['POST'])
@permission_classes([AllowAny])
def send_debit_fund_account_otp(request):
    amount = Decimal(request.data.get('amount'))
    currency = request.data.get('currency')
    public_api_key = request.data.get('public_api_key')
    account_id = request.data.get('account_id')
    security_code = request.data.get('security_code')
    created_at = request.data.get('created_at')
    print('sending otp ... currency:', currency)

    try:
        seller = get_object_or_404(
            User, Q(test_api_key=public_api_key) | Q(live_api_key=public_api_key))
    except User.DoesNotExist:
        return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
    print('seller:', seller)

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

    payer_email = user.email
    first_name = user.first_name
    formatted_payer_email = format_email(payer_email)
    print('formatted_payer_email:', formatted_payer_email)

    if public_api_key.startswith('live_'):
        if currency == "NGN":
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

            # Send email
            try:
                send_payer_fund_otp(request, payer_email, first_name)
            except Exception as e:
                print(e)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'Success', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)
            # send_ngn_debit_fund_account_otp(request, amount, currency, public_api_key, account_id, security_code, created_at)
        elif currency == "USD":
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

            # Send email
            try:
                send_payer_fund_otp(request, payer_email, first_name)
            except Exception as e:
                print(e)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response({'detail': 'Success', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)
            # send_usd_debit_fund_account_otp(request, amount, currency, public_api_key, account_id, security_code, created_at)
        else:
            return Response({'detail': 'Invalid currency format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'detail': 'Invalid API key format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_debit_fund_email_otp(request):
    print('verifying otp...')
    try:
        otp = request.data.get('otp')
        amount = Decimal(request.data.get('amount'))
        currency = request.data.get('currency')
        public_api_key = request.data.get('public_api_key')
        account_id = request.data.get('account_id')
        created_at = request.data.get('created_at')
        buyer_email = request.data.get('buyer_email')
        debit_account_id = generate_debit_account_id()
        print('sending otp ... currency:', currency)
        print('otp:', otp, )

        try:
            seller = get_object_or_404(
                User, Q(test_api_key=public_api_key) | Q(live_api_key=public_api_key))
        except User.DoesNotExist:
            return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
        print('seller:', seller)

        if public_api_key.startswith('test_'):
            verify_debit_test_account_fund(request, amount, currency, public_api_key, account_id, created_at, buyer_email, seller)
            print('verifying debit_test_account_fund...', created_at)

        elif public_api_key.startswith('live_'):
            try:
                buyer = User.objects.get(account_id=account_id)
            except User.DoesNotExist:
                return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
            print('buyer:', buyer)

            try:
                email_otp = EmailOtp.objects.get(email_otp=otp)
            except EmailOtp.DoesNotExist:
                return Response({'detail': 'Invalid OTP. Please try again.'}, status=status.HTTP_404_NOT_FOUND)
            
            if currency == "NGN":

                if email_otp.is_valid():
                    email_otp.delete()
                    try:
                        account_balance, created = AccountFundBalance.objects.get_or_create(
                            user=buyer)

                        old_bal = account_balance.balance
                        print('old balance:', old_bal)

                        if old_bal < amount:
                            return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
                        account_balance.balance -= amount
                        account_balance.save()
                        new_bal = account_balance.balance
                        print('new_bal:', new_bal)

                        debit_fund_account = DebitAccountFund.objects.create(
                            user=buyer,
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

                        amount = '{:,.0f}'.format(float(request.data.get('amount')))
                        print("\amount:", amount)
                        # send email
                        seller_email = seller.email
                        buyer_email = buyer.email
                        buyer_name = buyer.first_name
                        formatted_buyer_account_id = format_number(account_id)
                        print("\nbuyer_email:", buyer_email)
                        
                        try:
                            send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
                                buyer_email, buyer_name, formatted_buyer_account_id,  old_bal, new_bal, created_at)
                        except Exception as e:
                            print(e)
                            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
                    except DebitAccountFund.DoesNotExist:
                        return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
                # verify_ngn_account_debit_email_otp(request, otp, amount, account_id, currency, public_api_key, created_at)
            elif currency == "USD":
                try:
                    buyer = User.objects.get(account_id=account_id)
                except User.DoesNotExist:
                    return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
                print('buyer:', buyer)

                try:
                    email_otp = EmailOtp.objects.get(email_otp=otp)
                except EmailOtp.DoesNotExist:
                    return Response({'detail': 'Invalid OTP. Please try again.'}, status=status.HTTP_404_NOT_FOUND)

                if email_otp.is_valid():
                    email_otp.delete()
                    try:
                        account_balance, created = UsdAccountFundBalance.objects.get_or_create(
                            user=buyer)

                        old_bal = account_balance.balance
                        # old_bal = account_balance.balance
                        print('old_bal:', old_bal)

                        if old_bal < amount:
                            return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
                        account_balance.balance -= amount
                        account_balance.save()
                        new_bal = account_balance.balance
                        print('new_bal:', new_bal)

                        debit_fund_account = DebitUsdAccountFund.objects.create(
                            user=buyer,
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

                        try:
                            seller = User.objects.get(live_api_key=public_api_key)
                        except User.DoesNotExist:
                            return Response({'detail': 'Invalid or seller API Key not activated. Please contact the seller.'},
                                            status=status.HTTP_401_UNAUTHORIZED)

                        amount = '{:,.0f}'.format(float(amount))
                        old_bal = '{:,.0f}'.format(old_bal)
                        new_bal = '{:,.0f}'.format(new_bal)
                        print("\amount:", amount)
                        # send buyer transaction email
                        seller_email = seller.email
                        buyer_email = buyer.email
                        buyer_name = buyer.first_name
                        formatted_buyer_account_id = format_number(account_id)
                        print("\nbuyer_email:", buyer_email)
                        
                        try:
                            send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
                                buyer_email, buyer_name, formatted_buyer_account_id,  old_bal, new_bal, created_at)
                        except Exception as e:
                            print(e)
                            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                        return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
                    except DebitUsdAccountFund.DoesNotExist:
                        return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)
                # verify_usd_account_debit_email_otp(request, otp, amount, account_id, currency, public_api_key, created_at)
            else:
                return Response({'detail': 'Invalid currency format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'Invalid API key format. Please contact the seller.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid API key. Please contact the seller.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def send_ngn_debit_fund_account_otp(request, amount, currency, public_api_key, account_id, security_code, created_at):
#     print('currency:', currency)

#     try:
#         user = User.objects.get(account_id=account_id)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

#     try:
#         user = User.objects.get(security_code=security_code)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid or expired Security Code.'}, status=status.HTTP_404_NOT_FOUND)

#     if user is None:
#         return Response({'detail': 'Invalid Account ID or Security Code is expired.'}, status=status.HTTP_404_NOT_FOUND)

#     print('user:', user)

#     try:
#         account_balance = AccountFundBalance.objects.get(user=user)
#     except AccountFundBalance.DoesNotExist:
#         return Response({'detail': 'Account fund not found'}, status=status.HTTP_400_BAD_REQUEST)

#     if account_balance.is_diabled == True:
#         return Response({'detail': 'Account fund is currently diabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

#     if account_balance.is_active == False:
#         return Response({'detail': 'Account fund is currently inactive.'}, status=status.HTTP_400_BAD_REQUEST)

#     if account_balance.max_withdrawal is None:
#         return Response({'detail': 'Maximum account fund value is set to None. Please set a minimum value for the Account Fund.'}, status=status.HTTP_400_BAD_REQUEST)

#     if account_balance.max_withdrawal < amount:
#         return Response({'detail': 'Maximum account fund withrawal exceeded.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         seller = User.objects.filter(Q(test_api_key=public_api_key) | Q(
#             live_api_key=public_api_key)).first()
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid or Seller API Key not found. Please contact the seller.'}, status=status.HTTP_401_UNAUTHORIZED)
#     print('seller:', seller)

#     payer_email = user.email
#     first_name = user.first_name
#     formatted_payer_email = format_email(payer_email)
#     print('payer_email:', payer_email, 'first_name:', first_name,
#           'formatted_payer_email:', formatted_payer_email)

#     # Send email
#     try:
#         send_payer_account_fund_otp(request, payer_email, first_name)
#     except Exception as e:
#         print(e)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response({'detail': 'Success', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)


# def send_ngn_debit_fund_account_otp(request, amount, currency, public_api_key, account_id, security_code, created_at):
#     print('currency:', currency)

#     try:
#         user = User.objects.get(account_id=account_id)
#     except User.DoesNotExist:
#         return {'detail': 'Invalid Account ID.', 'status': status.HTTP_404_NOT_FOUND}

#     try:
#         user = User.objects.get(security_code=security_code)
#     except User.DoesNotExist:
#         return {'detail': 'Invalid or expired Security Code.', 'status': status.HTTP_404_NOT_FOUND}

#     if user is None:
#         return {'detail': 'Invalid Account ID or Security Code is expired.', 'status': status.HTTP_404_NOT_FOUND}

#     print('user:', user)

#     try:
#         account_balance = AccountFundBalance.objects.get(user=user)
#     except AccountFundBalance.DoesNotExist:
#         return {'detail': 'Account fund not found.', 'status': status.HTTP_400_BAD_REQUEST}

#     if account_balance.is_disabled:
#         return {'detail': 'Account fund is currently disabled. Please contact support.', 'status': status.HTTP_400_BAD_REQUEST}

#     if not account_balance.is_active:
#         return {'detail': 'Account fund is currently inactive.', 'status': status.HTTP_400_BAD_REQUEST}

#     if account_balance.max_withdrawal is None:
#         return {'detail': 'Maximum account fund value is set to None. Please set a minimum value for the Account Fund.', 'status': status.HTTP_400_BAD_REQUEST}

#     if account_balance.max_withdrawal < amount:
#         return {'detail': 'Maximum account fund withdrawal exceeded.', 'status': status.HTTP_400_BAD_REQUEST}

#     try:
#         seller = User.objects.get(live_api_key=public_api_key)
#     except User.DoesNotExist:
#         return {'detail': 'Invalid or Seller API Key not found. Please contact the seller.', 'status': status.HTTP_401_UNAUTHORIZED}
#     print('seller:', seller)

#     payer_email = user.email
#     first_name = user.first_name
#     formatted_payer_email = format_email(payer_email)
#     print('payer_email:', payer_email, 'first_name:', first_name, 'formatted_payer_email:', formatted_payer_email)

#     # Send email
#     try:
#         send_payer_account_fund_otp(request, payer_email, first_name)
#     except Exception as e:
#         print(e)
#         return {'detail': str(e), 'status': status.HTTP_500_INTERNAL_SERVER_ERROR}
    
#     return {'detail': 'Success', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email, 'status': status.HTTP_200_OK}



def send_payer_fund_otp(request, payer_email, first_name):
    print('first_name:', first_name, 'payer_email:',  payer_email)

    email_otp, created = EmailOtp.objects.get_or_create(email=payer_email)
    email_otp.generate_email_otp()
    print('email_otp:', email_otp, "email_otp:", email_otp.email_otp)

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration))
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
        return {'detail': str(e), 'status': 500}


# def verify_ngn_account_debit_email_otp(request, otp, amount, account_id, currency, public_api_key, created_at):
#     debit_account_id = generate_debit_account_id()
#     print('otp:', otp, )

#     try:
#         user = User.objects.get(account_id=account_id)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
#     print('user:', user)

#     try:
#         email_otp = EmailOtp.objects.get(email_otp=otp)
#     except EmailOtp.DoesNotExist:
#         return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_404_NOT_FOUND)

#     if email_otp.is_valid():
#         email_otp.delete()

#         try:
#             account_balance, created = AccountFundBalance.objects.get_or_create(
#                 user=user)

#             # balance = account_balance.balance
#             old_bal = account_balance.balance
#             print('old balance:', old_bal)

#             if old_bal < amount:
#                 return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
#             account_balance.balance -= amount
#             account_balance.save()
#             print('new balance:', account_balance.balance)

#             debit_fund_account = DebitAccountFund.objects.create(
#                 user=user,
#                 amount=amount,
#                 currency=currency,
#                 old_bal=old_bal,
#                 # payment_method=payment_method,
#                 # payment_provider=payment_provider,
#                 debit_account_id=debit_account_id,
#             )
#             debit_fund_account.is_success = True
#             debit_fund_account.new_bal = account_balance.balance
#             debit_fund_account.save()

#             try:
#                 seller = User.objects.get(live_api_key=public_api_key)
#             except User.DoesNotExist:
#                 return Response({'detail': 'Invalid or seller API Key not activated. Please contact the seller.'},
#                                 status=status.HTTP_401_UNAUTHORIZED)

#             try:
#                 buyer = User.objects.get(account_id=account_id)
#             except User.DoesNotExist:
#                 return Response({'detail': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)

#             amount = '{:,.0f}'.format(float(request.data.get('amount')))
#             print("\amount:", amount)
#             # send buyer transaction email
#             seller_email = seller.email
#             # seller_name = "sellangle.com"
#             buyer_email = buyer.email
#             buyer_name = buyer.first_name
#             formatted_buyer_account_id = format_number(account_id)
#             print("\nbuyer_email:", buyer_email)
            
#             try:
#                 send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
#                                                     buyer_email, buyer_name, formatted_buyer_account_id, created_at)
#             except Exception as e:
#                 print(e)
#                 return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#             return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
#         except DebitAccountFund.DoesNotExist:
#             return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


def send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
                                buyer_email, buyer_name, formatted_buyer_account_id, old_bal, new_bal, created_at):
    print("Sending debit alert email...")
    try:
        subject = f"Paysofter Account Fund Debit Alert of {amount} {currency} with Debit Fund ID [{debit_account_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Account Fund Debit Alert</title>
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
                            <h2>Paysofter Account Fund Debit Alert</h2>
                        </div>
                        <div class="content">
                            <p>Dear {buyer_name.title()},</p>
                            <p>This is to inform you that your Paysofter Account Fund with account ID: ({formatted_buyer_account_id}) 
                            has been debited with 
                            <strong>{amount} {currency}</strong> being payment made to <b>{seller_email}</b> with a <b>Debit Fund ID: 
                            "{debit_account_id}"</b> at <b>{created_at}</b>.</p>
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
                                    <td>Debit Fund ID</td>
                                    <td>{debit_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Old Bal</td>
                                    <td>{old_bal}  {currency}</td>
                                </tr>
                                <tr>
                                    <td>New Bal</td>
                                    <td>{new_bal}  {currency}</td>
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
        to = [{"email": buyer_email, "name": buyer_name}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


# def send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
#                                                     seller_name, buyer_email, buyer_name, formatted_buyer_account_id, created_at):
#     print("Sending debit alert email...")
#     try:
#         subject = f"Paysofter Account Fund Debit Alert of {amount} {currency} with Debit Fund ID [{debit_account_id}]"
#         html_content = f"""
#                 <!DOCTYPE html>
#                 <html>
#                 <head>
#                     <title>Paysofter Account Fund Debit Alert</title>
#                     <style>
#                         body {{
#                             font-family: Arial, sans-serif;
#                             line-height: 1.6;
#                             color: #333;
#                         }}
#                         .container {{
#                             max-width: 600px;
#                             margin: 0 auto;
#                         }}
#                         .header {{
#                             background-color: #FF0000;;
#                             color: white;
#                             padding: 1em;
#                             text-align: center;
#                         }}
#                         .content {{
#                             padding: 1em;
#                         }}
#                         .footer {{
#                             background-color: #f1f1f1;
#                             padding: 1em;
#                             text-align: center;
#                         }}
#                         .button {{
#                             display: inline-block;
#                             background-color: #e53935; /* Red background color */
#                             color: #fff;
#                             padding: 10px 20px;
#                             text-decoration: none;
#                             border-radius: 5px; /* Rounded corners */
#                         }}
#                     </style>
#                 </head>
#                 <body>
#                     <div class="container">
#                         <div class="header">
#                             <h2>Paysofter Account Fund Debit Alert</h2>
#                         </div>
#                         <div class="content">
#                             <p>Dear {buyer_name.title()},</p>
#                             <p>This is to inform you that your Paysofter Account Fund with account ID: ({formatted_buyer_account_id}) has been debited with 
#                             <strong>{amount} {currency}</strong> being payment made to <b>{seller_email}</b> with a <b>Debit Fund ID: 
#                             "{debit_account_id}"</b> at <b>{created_at}</b>.</p>
#                             <p>If you have received this email in error, please ignore it.</p>
#                             <p>Best regards,</p>
#                             <p>Paysofter Inc.</p>
#                         </div>
#                         <div class="footer">
#                             <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
#                             <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
#                         </div>
#                     </div>
#                 </body>
#                 </html>
#             """
#         html_content=html_content,
#         subject=subject
#         to = [{"email": buyer_email}]
#         send_email_sendinblue(subject, html_content, to)
#     except Exception as e:
#         print(e)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_debits(request):
    user = request.user
    try:
        account_debits = DebitAccountFund.objects.filter(
            user=user).order_by('-timestamp')
        serializer = DebitAccountFundSerializer(account_debits, many=True)
        return Response(serializer.data)
    except DebitAccountFund.DoesNotExist:
        return Response({'detail': 'Debit account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_account_fund_balance(request):
    try:
        account_fund_balance, created = AccountFundBalance.objects.get_or_create(
            user=request.user)
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
        serializer = AccountFundBalanceSerializer(
            account_fund_balance, many=True)
        return Response(serializer.data)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Fund account balance not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_funds(request):
    user = request.user
    try:
        account_funds = FundAccount.objects.filter(
            user=user).order_by('-timestamp')
        serializer = FundAccountSerializer(account_funds, many=True)
        return Response(serializer.data)
    except FundAccount.DoesNotExist:
        return Response({'detail': 'Fund account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_funds_debits(request):
    user = request.user
    try:
        account_funds = DebitAccountFund.objects.filter(
            user=user).order_by('-timestamp')
        serializer = DebitAccountFundSerializer(account_funds, many=True)
        return Response(serializer.data)
    except DebitAccountFund.DoesNotExist:
        return Response({'detail': 'Fund account debits not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_account_funds_credits(request):
    user = request.user
    try:
        account_funds = FundAccount.objects.filter(
            user=user).order_by('-timestamp')
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
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration))
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
        account_balance = AccountFundBalance.objects.get(
            user=account_fund_user)
    except AccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    account_balance.is_diabled = False
    account_balance.is_active = False
    account_balance.save()

    try:
        usd_account_balance = UsdAccountFundBalance.objects.get(
            user=account_fund_user)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'Account fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    usd_account_balance.is_diabled = False
    usd_account_balance.is_active = False
    usd_account_balance.save()

    print(f'Account fund deactivated.')
    return Response({'detail': f'Account fund activated.', }, status=status.HTTP_200_OK)


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
        fund_account_balance, created = UsdAccountFundBalance.objects.get_or_create(
            user=user)
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

        new_bal = fund_account_balance.balance

        # send email
        amount = '{:,.0f}'.format(float(amount))
        print("\amount:", amount)
        old_bal = '{:,.0f}'.format(old_bal)
        new_bal = '{:,.0f}'.format(new_bal)
        user_email = user.email
        first_name = user.first_name

        try:
            send_fund_credit_alert_email(request, amount, currency, fund_account_id, created_at, user_email, first_name, old_bal, new_bal)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # # send email
        # amount = '{:,.0f}'.format(float(request.data.get('amount')))
        # print("\amount:", amount)
        # sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        # sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
        # user_email = user.email
        # first_name = user.first_name

        # print("\nsender_email:", sender_email, "user_email:", user_email)

        # try:
        #     send_usd_user_email(request, sender_name, sender_email, amount,
        #                         currency, fund_account_id, created_at, user_email, first_name)
        # except Exception as e:
        #     print(e)
        #     return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': f'Fund account request submitted successfully. Old Bal: NGN {old_bal}'},
                        status=status.HTTP_201_CREATED)
    except FundUsdAccount.DoesNotExist:
        return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def send_usd_user_email(request, sender_name, sender_email, amount, currency, fund_account_id, created_at, user_email, first_name):
#     # Email Sending API Config
#     configuration = sib_api_v3_sdk.Configuration()
#     configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
#     api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
#         sib_api_v3_sdk.ApiClient(configuration))

#     # Sending email
#     print("\nSending email...")
#     subject = f"[TEST MODE] Notice of Paysofter account fund of {amount} {currency} with  Account Fund ID [{fund_account_id}]"
#     html_content = f"""
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <title>Paysofter Receipt</title>
#             </head>
#             <body>
#                 <p>Dear {first_name},</p>
#                 <p>You have funded your Paysofter account with <strong>{amount} {currency}</strong> with  <b>Account Fund ID: "{fund_account_id}"</b> at <b>{created_at}</b>.</p>
#                 <p>If you have any issue with the payment, kindly reply this email.</b></p>
#                 <p>If you have received this email in error, please ignore it.</p>
#                 <p>Best regards,</p>
#                 <p>Paysofter Inc.</p>
#             </body>
#             </html>
#         """
#     sender = {"name": sender_name, "email": sender_email}
#     to = [{"email": user_email}]
#     send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#         to=to,
#         html_content=html_content,
#         sender=sender,
#         subject=subject
#     )
#     try:
#         api_response = api_instance.send_transac_email(send_smtp_email)
#         print("Email sent!")
#     except ApiException as e:
#         print(e)
#         return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def send_usd_debit_fund_account_otp(request, amount, currency, public_api_key, account_id, security_code, created_at):
#     print('currency:', currency)

#     try:
#         user = User.objects.get(account_id=account_id)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)

#     try:
#         user = User.objects.get(security_code=security_code)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid or expired Security Code.'}, status=status.HTTP_404_NOT_FOUND)

#     if user is None:
#         return Response({'detail': 'Invalid Account ID or Security Code is expired.'}, status=status.HTTP_404_NOT_FOUND)

#     print('user:', user)

#     try:
#         usd_account_balance = UsdAccountFundBalance.objects.get(user=user)
#     except UsdAccountFundBalance.DoesNotExist:
#         return Response({'detail': 'Account fund not found'}, status=status.HTTP_400_BAD_REQUEST)

#     if usd_account_balance.is_diabled == True:
#         return Response({'detail': 'Account fund is currently diabled. Please contact support.'}, status=status.HTTP_400_BAD_REQUEST)

#     if usd_account_balance.is_active == False:
#         return Response({'detail': 'Account fund is currently inactive.'}, status=status.HTTP_400_BAD_REQUEST)

#     if usd_account_balance.max_withdrawal is None:
#         return Response({'detail': 'Maximum account fund value is set to None. Please set a minimum value for the Account Fund.'}, status=status.HTTP_400_BAD_REQUEST)

#     if usd_account_balance.max_withdrawal < amount:
#         return Response({'detail': 'Maximum account fund withrawal exceeded.'}, status=status.HTTP_400_BAD_REQUEST)

#     try:
#         seller = User.objects.get(live_api_key=public_api_key)
#         # seller = User.objects.filter(Q(test_api_key=public_api_key) | Q(
#         #     live_api_key=public_api_key)).first()
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid or Seller API Key not found. Please contact the seller.'}, status=status.HTTP_401_UNAUTHORIZED)
#     print('seller:', seller)

#     payer_email = user.email
#     first_name = user.first_name
#     formatted_payer_email = format_email(payer_email)
#     print('payer_email:', payer_email, 'first_name:', first_name,
#           'formatted_payer_email:', formatted_payer_email)

#     # Send email
#     try:
#         send_usd_payer_account_fund_otp(request, payer_email, first_name)
#     except Exception as e:
#         print(e)
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#     return Response({'detail': 'Success', 'formattedPayerEmail': formatted_payer_email, 'payerEmail': payer_email}, status=status.HTTP_200_OK)


# def send_usd_payer_account_fund_otp(request, payer_email, first_name):
#     print('first_name:', first_name, 'payer_email:',  payer_email)

#     email_otp, created = EmailOtp.objects.get_or_create(email=payer_email)
#     email_otp.generate_email_otp()
#     print('email_otp:', email_otp, "email_otp:", email_otp.email_otp)

#     # Email Sending API Config
#     configuration = sib_api_v3_sdk.Configuration()
#     configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
#     api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
#         sib_api_v3_sdk.ApiClient(configuration))
#     # Sending email
#     subject = "Account Fund Payment OTP"
#     print("\nSending email OTP...")
#     html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <title>OTP Account Fund Payment</title>
#         </head>
#         <body>
#             <p>Dear {first_name.title()},</p>
#             <p>To complete this payment using Paysofter Account Fund, please use the OTP provided below:</p>
#             <h2>OTP: {email_otp.email_otp}</h2>
#             <p>This OTP is valid for 10 minutes.</p>
#             <p>If you didn't request this OTP, please ignore it.</p>
#             <p>Best regards,</p>
#             <p>Paysofter Inc.</p>
#         </body>
#         </html>
#     """
#     sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
#     sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
#     sender = {"name": sender_name, "email": sender_email}
#     to = [{"email": payer_email, "name": first_name}]
#     send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
#         to=to,
#         html_content=html_content,
#         sender=sender,
#         subject=subject
#     )
#     try:
#         api_response = api_instance.send_transac_email(send_smtp_email)
#         print("Email sent!")
#     except ApiException as e:
#         print(e)
#         return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def verify_usd_account_debit_email_otp(request, otp, amount, account_id, currency, public_api_key, created_at):
#     debit_account_id = generate_debit_account_id()
#     print('otp:', otp)

#     try:
#         user = User.objects.get(account_id=account_id)
#     except User.DoesNotExist:
#         return Response({'detail': 'Invalid Account ID'}, status=status.HTTP_404_NOT_FOUND)
#     print('user:', user)

#     try:
#         email_otp = EmailOtp.objects.get(email_otp=otp)
#     except EmailOtp.DoesNotExist:
#         return Response({'detail': 'Invalid OTP.'}, status=status.HTTP_404_NOT_FOUND)

#     if email_otp.is_valid():
#         email_otp.delete()
#         try:
#             account_balance, created = UsdAccountFundBalance.objects.get_or_create(
#                 user=user)

#             old_bal = account_balance.balance
#             # old_bal = account_balance.balance
#             print('old balance:', old_bal)

#             if old_bal < amount:
#                 return Response({'detail': 'Insufficient account balance.'}, status=status.HTTP_404_NOT_FOUND)
#             account_balance.balance -= amount
#             account_balance.save()
#             print('new balance:', account_balance.balance)

#             debit_fund_account = DebitUsdAccountFund.objects.create(
#                 user=user,
#                 amount=amount,
#                 currency=currency,
#                 old_bal=old_bal,
#                 # payment_method=payment_method,
#                 # payment_provider=payment_provider,
#                 debit_account_id=debit_account_id,
#             )
#             debit_fund_account.is_success = True
#             debit_fund_account.new_bal = account_balance.balance
#             debit_fund_account.save()

#             try:
#                 seller = User.objects.get(live_api_key=public_api_key)
#             except User.DoesNotExist:
#                 return Response({'detail': 'Invalid or seller API Key not activated. Please contact the seller.'},
#                                 status=status.HTTP_401_UNAUTHORIZED)

#             try:
#                 buyer = User.objects.get(account_id=account_id)
#             except User.DoesNotExist:
#                 return Response({'detail': 'Buyer not found'}, status=status.HTTP_404_NOT_FOUND)

#             amount = '{:,.0f}'.format(float(request.data.get('amount')))
#             print("\amount:", amount)
#             # send buyer transaction email
#             seller_email = seller.email
#             seller_name = "sellangle.com"
#             buyer_email = buyer.email
#             buyer_name = buyer.first_name
#             formatted_buyer_account_id = format_number(account_id)
#             print("\nbuyer_email:", buyer_email)
            
#             try:
#                 send_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
#                                                     seller_name, buyer_email, buyer_name, formatted_buyer_account_id, created_at)
#             except Exception as e:
#                 print(e)
#                 return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             return Response({'success': f'Account debited successfully.'}, status=status.HTTP_201_CREATED)
#         except DebitUsdAccountFund.DoesNotExist:
#             return Response({'detail': 'Debit Fund account not found'}, status=status.HTTP_404_NOT_FOUND)
#     else:
#         return Response({'detail': 'Invalid or expired OTP. Please try again.'}, status=status.HTTP_400_BAD_REQUEST)


def verify_debit_test_account_fund(request, amount, currency, public_api_key, account_id, created_at, buyer_email, seller):
    print('verify debit_test_account_fund:', seller)

    debit_account_id = generate_debit_account_id()

    try:
        debit_fund_account = TestDebitAccountFund.objects.create(
            # user=user,
            amount=amount,
            currency=currency,
            # old_bal=old_bal,
            # payment_method=payment_method,
            # payment_provider=payment_provider,
            debit_account_id=debit_account_id,
        )
        debit_fund_account.is_success = True
        # debit_fund_account.new_bal = account_balance.balance
        debit_fund_account.save()

        amount = '{:,.0f}'.format(float(request.data.get('amount')))
        old_bal = 0.00
        new_bal = 0.00
        print("\amount:", amount)
        # send buyer transaction email
        # sender_name = settings.PAYSOFTER_EMAIL_SENDER_NAME
        # sender_email = settings.PAYSOFTER_EMAIL_HOST_USER
        # buyer_email = buyer_email
        seller_email = seller.email
        # seller_name = "sellangle.com"
        formatted_buyer_account_id = format_number(account_id)

        print("\nbuyer_email:", buyer_email)
        
        try:
            send_test_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
                                                buyer_email, formatted_buyer_account_id, old_bal, new_bal, created_at)
        except Exception as e:
            print(e)
            return {'detail': str(e), 'status': 500}
        return {'detail': 'created successfully', 'status': 201}
    
    except TestDebitAccountFund.DoesNotExist:
        return {'detail': 'not found', 'status': 404}


def send_test_fund_debit_alert_email(request, amount, currency, seller_email, debit_account_id, 
                                                buyer_email, formatted_buyer_account_id, old_bal, new_bal, created_at):
    print("Sending test debit alert email...")
    try:
        subject = f"[TEST MODE] Paysofter Account Fund Debit Alert of {amount} {currency} with Debit Fund ID [{debit_account_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Account Fund Debit Alert</title>
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
                            <h2>Paysofter Account Fund Debit Alert</h2>
                        </div>
                        <div class="content">
                            <p>Dear valued customer,</p>
                            <p>This is to inform you that your Paysofter Account Fund with account ID: ({formatted_buyer_account_id}) 
                            has been debited with 
                            <strong>{amount} {currency}</strong> being payment made to <b>{seller_email}</b> with a <b>Debit Fund ID: 
                            "{debit_account_id}"</b> at <b>{created_at}</b>.</p>
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
                                    <td>Debit Fund ID</td>
                                    <td>{debit_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                <tr>
                                    <td>Buyer Account ID</td>
                                    <td>{formatted_buyer_account_id}</td>
                                </tr>
                                <tr>
                                    <td>Old Bal</td>
                                    <td>{old_bal}  {currency}</td>
                                </tr>
                                <tr>
                                    <td>New Bal</td>
                                    <td>{new_bal}  {currency}</td>
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
                            <p>Note: This is a mock transaction as no real money is debited from your account.</p>
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content=html_content,
        subject=subject
        to = [{"email": buyer_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}       


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_user_usd_account_fund_balance(request):
    try:
        account_fund_balance, created = UsdAccountFundBalance.objects.get_or_create(
            user=request.user)
        serializer = UsdAccountFundBalanceSerializer(account_fund_balance)
        return Response(serializer.data)
    except UsdAccountFundBalance.DoesNotExist:
        return Response({'detail': 'USD fund account balance not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_usd_account_fund_credits(request):
    user = request.user
    try:
        account_funds = FundUsdAccount.objects.filter(
            user=user).order_by('-timestamp')
        serializer = FundUsdAccountSerializer(account_funds, many=True)
        return Response(serializer.data)
    except FundUsdAccount.DoesNotExist:
        return Response({'detail': 'USD account funds not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_usd_account_debits(request):
    user = request.user
    try:
        account_debits = DebitUsdAccountFund.objects.filter(
            user=user).order_by('-timestamp')
        serializer = DebitUsdAccountFundFundSerializer(
            account_debits, many=True)
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
