# promise/views.py
import random
import string
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.views import APIView

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


from .models import PaysofterPromise, PromiseMessage
from .serializers import (PaysofterPromiseSerializer,
                          PromiseMessageSerializer,
                          )


from send_email_otp.serializers import EmailOTPSerializer
from send_email_otp.models import EmailOtp

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_promise_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'PRO'+''.join(random.choices(letters_and_digits, k=17))


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
    print('account_id:', account_id)

    try:
        seller = User.objects.get(test_api_key=public_api_key)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or seller API Key not activated. Please contact the seller.'}, status=status.HTTP_401_UNAUTHORIZED)
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
            # duration_hours=duration_hours,
            # payment_method=payment_method,
            # payment_provider=payment_provider,
            promise_id=promise_id,
            is_active=True
        )

        if promise.duration:
            if promise.duration == '0 day':
                promise.duration_hours = timedelta(hours=0)
            elif promise.duration == 'Within 1 day':
                promise.duration_hours = timedelta(hours=24)
            elif promise.duration == '2 days':
                promise.duration_hours = timedelta(days=2)
            elif promise.duration == '3 days':
                promise.duration_hours = timedelta(days=3)
            elif promise.duration == '5 days':
                promise.duration_hours = timedelta(days=5)
            elif promise.duration == '1 week':
                promise.duration_hours = timedelta(weeks=1)
            elif promise.duration == '2 weeks':
                promise.duration_hours = timedelta(weeks=2)
            elif promise.duration == '1 month':
                promise.duration_hours = timedelta(days=30)

            promise.expiration_date = timezone.now() + promise.duration_hours

        promise.is_success = True
        promise.save()

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

        print("\nsender_email:", sender_email, "formatted_seller_account_id:",
              formatted_seller_account_id, "formatted_buyer_account_id:", formatted_buyer_account_id)

        try:
            send_buyer_email(request, sender_name, sender_email, amount, currency, promise_id,
                             created_at, buyer_email, buyer_first_name, formatted_seller_account_id)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            send_seller_email(request, sender_name, sender_email, amount, currency, promise_id,
                              created_at, seller_email, seller_first_name, formatted_buyer_account_id)
        except Exception as e:
            print(e)
            return Response({'error': 'Error sending email.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'success': f'Promise created successfully.'},
                        status=status.HTTP_201_CREATED)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Fund account request not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def send_buyer_email(request, sender_name, sender_email, amount, currency, promise_id, created_at, buyer_email, buyer_first_name, formatted_seller_account_id):
    url = settings.PAYSOFTER_URL
    buyer_confirm_promise_link = f"{url}/promise/buyer"

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    # subject =  f"[TEST MODE] Notice of Paysofter Promise Alert of NGN {amount} with  Promise ID [{promise_id}]"
    subject = f"Paysofter Promise Alert"
    buyer_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Promise Alert</title>
            </head>
            <body>
                <p>Hello {buyer_first_name.title()},</p>
                <p>This is to inform you that you have made a promise of <strong>{amount} {currency}</strong> with <b>Promise ID: "{promise_id}"</b> to a seller with Account ID: "<strong>{formatted_seller_account_id}</strong>" at <b>{created_at}</b>.</p>
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


def send_seller_email(request, sender_name, sender_email, amount, currency, promise_id, created_at, seller_email, seller_first_name, formatted_buyer_account_id):
    url = settings.PAYSOFTER_URL
    seller_confirm_promise_link = f"{url}/promise/seller"

    # Email Sending API Config
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration))

    # Sending email
    print("\nSending email...")
    # subject =  f"[TEST MODE] Notice of Paysofter Promise of NGN {amount} with  Promise ID [{promise_id}]"
    subject = f"Paysofter Promise Alert"
    seller_html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Paysofter Promise Alert</title>
            </head>
            <body>
                <p>Hello {seller_first_name.title()},</p>
                <p>This is to inform you that you have received a promise of <strong>{amount} {currency}</strong> with <b>Promise ID: "{promise_id}"</b> from a buyer with Account ID: "<strong>{formatted_buyer_account_id}</strong>" at <b>{created_at}</b>.</p>
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buyer_confirm_promise(request):
    user = request.user
    data = request.data
    print('data:', data)

    promise_id = data.get('promise_id')
    password = data.get('password')
    # promise_id = request.data.get('promise_id')
    # password = request.data.get('password')
    print('promise_id:', promise_id)

    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        promise = PaysofterPromise.objects.get(
            buyer=user, promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_400_BAD_REQUEST)

    print('buyer_promise_fulfilled(before):', promise.buyer_promise_fulfilled)

    promise.buyer_promise_fulfilled = True
    promise.is_success = True
    promise.is_active = False
    promise.duration = '0 day'
    promise.status = "Fulfilled"
    promise.save()
    print('buyer_promise_fulfilled(after):', promise.buyer_promise_fulfilled)
    return Response({'detail': 'Promise fulfilled.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seller_confirm_promise(request):
    user = request.user
    data = request.data
    print('data:', data)
    print('seller:', user)

    promise_id = request.data.get('promise_id')
    print('promise_id:', promise_id)

    try:
        promise = PaysofterPromise.objects.get(
            seller=user, promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_400_BAD_REQUEST)

    print('seller_fulfilled_promise(before):',
          promise.seller_fulfilled_promise)

    promise.seller_fulfilled_promise = True
    promise.save()
    print('seller_fulfilled_promise(after):', promise.seller_fulfilled_promise)
    return Response({'detail': 'Promise fulfilled.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def settle_disputed_promise(request):
    user = request.user
    data = request.data
    print('data:', data)

    promise_id = data.get('promise_id')
    keyword = data.get('keyword')
    print('promise_id:', promise_id)

    if keyword != "confirm":
        return Response({'detail': 'Invalid keyword entered.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        promise = PaysofterPromise.objects.get(
            Q(buyer=user) | Q(seller=user),
            promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_400_BAD_REQUEST)

    print('is_settle_conflict_activated(before):',
          promise.is_settle_conflict_activated)

    promise.is_settle_conflict_activated = True
    print('is_settle_conflict_activated(after):',
          promise.is_settle_conflict_activated)
    promise.save()
    return Response({'detail': 'Settle disputed promise activated.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_buyer_promises(request):
    user = request.user
    try:
        promise = PaysofterPromise.objects.filter(
            buyer=user).order_by('-timestamp')
        serializer = PaysofterPromiseSerializer(promise, many=True)
        return Response(serializer.data)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_promises(request):
    user = request.user
    try:
        promise = PaysofterPromise.objects.filter(
            seller=user).order_by('-timestamp')
        serializer = PaysofterPromiseSerializer(promise, many=True)
        return Response(serializer.data)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def get_all_promises(request):
    try:
        promise = PaysofterPromise.objects.filter().order_by('-timestamp')
        serializer = PaysofterPromiseSerializer(promise, many=True)
        return Response(serializer.data)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def cancel_promise(request):
    data = request.data
    user = request.user
    print('data:', data)

    promise_id = data.get('promise_id')
    password = data.get('password')

    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        promise = PaysofterPromise.objects.get(promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    promise.is_cancelled = True
    promise.is_delivered = False
    promise.is_active = False
    promise.is_success = False
    promise.status = 'Cancelled'

    promise.save()

    return Response({'detail': f'Promise cancelled.', }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buyer_create_promise_message(request):
    buyer = request.user
    data = request.data
    print('data:', data, 'buyer:', buyer)

    promise_id = data.get('promise_id')
    message = data.get('message')
    print('promise_id:', promise_id)
    print('message:', message)

    try:
        promise = PaysofterPromise.objects.get(promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    promise_message = PromiseMessage.objects.create(
        buyer=buyer,
        promise_message=promise,
        message=message,
    )

    if promise:
        promise.seller_msg_count += 1
        promise.message = message
        promise.modified_at = timezone.now()
        promise.save()

    return Response({'message': 'Promise message created'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seller_create_promise_message(request):
    seller = request.user
    data = request.data
    print('data:', data, 'seller:', seller)

    promise_id = data.get('promise_id')
    message = data.get('message')
    print('promise_id:', promise_id)
    print('message:', message)

    try:
        promise = PaysofterPromise.objects.get(promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    promise_message = PromiseMessage.objects.create(
        seller=seller,
        promise_message=promise,
        message=message,
    )

    if promise:
        promise.buyer_msg_count += 1
        promise.message = message
        promise.modified_at = timezone.now()
        promise.save()

    return Response({'message': 'Promise message created'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_buyer_promise_messages(request, promise_id):
    buyer = request.user
    # data  = request.data
    # print('data:', data)
    print('user:', buyer)

    # promise_id = data.get('promise_id')
    # print('promise_id:', promise_id)

    try:
        promise_message = PaysofterPromise.objects.get(
            promise_id=promise_id
        )
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    print('promise_message:', promise_message)

    try:
        promise_message = PromiseMessage.objects.filter(
            promise_message=promise_message,
        ).order_by('timestamp')
        serializer = PromiseMessageSerializer(promise_message, many=True)
        return Response(serializer.data)
    except PromiseMessage.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_seller_promise_messages(request, promise_id):
    seller = request.user
    # data  = request.data
    # print('data:', data)
    print('user:', seller)

    # promise_id = data.get('promise_id')
    # print('promise_id:', promise_id)

    try:
        promise_message = PaysofterPromise.objects.get(
            promise_id=promise_id
        )
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    print('promise_message:', promise_message)

    try:
        promise_message = PromiseMessage.objects.filter(
            promise_message=promise_message,
        ).order_by('timestamp')
        serializer = PromiseMessageSerializer(promise_message, many=True)
        return Response(serializer.data)
    except PromiseMessage.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_seller_promise_message_counter(request):
    buyer = request.user
    data = request.data
    print('data:', data, 'buyer:', buyer)

    promise_id = data.get('promise_id')
    print('promise_id:', promise_id)

    try:
        promise = PaysofterPromise.objects.get(promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    if promise.seller_msg_count > 0:
        promise.seller_msg_count = 0
        promise.save()
        print('seller_msg_count (cleared):', promise.seller_msg_count)

    return Response({'message': 'Promise message cleared.'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_buyer_promise_message_counter(request):
    seller = request.user
    data = request.data
    print('data:', data, 'seller:', seller)

    promise_id = data.get('promise_id')
    print('promise_id:', promise_id)

    try:
        promise = PaysofterPromise.objects.get(promise_id=promise_id)
    except PaysofterPromise.DoesNotExist:
        return Response({'detail': 'Promise message not found'}, status=status.HTTP_404_NOT_FOUND)

    if promise.buyer_msg_count > 0:
        promise.buyer_msg_count = 0
        promise.save()
        print('buyer_msg_count (cleared):', promise.buyer_msg_count)

    return Response({'message': 'Promise message cleared.'}, status=status.HTTP_200_OK)


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
