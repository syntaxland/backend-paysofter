from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
 
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from .models import EmailOtp
from user_profile.serializers import UserSerializer
from .serializers import EmailOTPSendSerializer

from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model

User = get_user_model()

 
@api_view(['POST'])
@permission_classes([AllowAny])
def send_email_otp(request):
    data=request.data
    serializer = EmailOTPSendSerializer(data=data)
    # email = serializer.validated_data['email']
    # first_name = serializer.validated_data['first_name']
    email = data.get('email')
    first_name = data.get('first_name')
    if serializer.is_valid():
        
        try:
            # Send email OTP
            email_otp, created = EmailOtp.objects.get_or_create(email=email)
            # if not created:
            email_otp.generate_email_otp()
            # Email Sending API Config
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            # Sending email
            subject = "OTP Email Verification"
            print("\nSending email OTP...")
            first_name = data['first_name'].title() if data.get('first_name') else 'User'
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OTP Email Verification</title>
                </head>
                <body>
                    <p>Dear {first_name.title()},</p>
                    <p>Thank you for signing up with our service.
                    To complete your registration, please use the OTP provided below:</p><br/>
                    <h2>OTP: {email_otp.email_otp}</h2><br/>
                    <p>This OTP is valid for 30 minutes.</p>
                    <p>If you didn't request this verification email, please ignore it.</p>
                    <p>Best regards,<br>Paysofter Inc.</p>
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
                print('\nOTP sent:', email_otp.email_otp)
            except ApiException as e:
                print(e)
            return Response({'detail': 'Email verification OTP sent successfully.'}, status=status.HTTP_200_OK)
        except EmailOtp.DoesNotExist:
            return Response({'detail': 'User not found. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_email_otp(request):
    data=request.data
    serializer = EmailOTPSendSerializer(data=data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        first_name = serializer.validated_data['first_name']
        try:
            # Send email OTP
            email_otp, created = EmailOtp.objects.get_or_create(email=email)
            # if not created:
            email_otp.generate_email_otp()
            # Email Sending API Config
            configuration = sib_api_v3_sdk.Configuration()
            configuration.api_key['api-key'] = settings.SENDINBLUE_API_KEY
            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
            # Sending email
            subject = "OTP Email Verification"
            print("\nResending email OTP...")
            first_name = data['first_name'].title() if data.get('first_name') else 'User'
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OTP Email Verification</title>
                </head>
                <body>
                    <p>Dear {first_name.title()},</p>
                    <p>Thank you for signing up with our service.
                    To complete your registration, please use the OTP provided below:</p><br/>
                    <h2>OTP: {email_otp.email_otp}</h2><br/>
                    <p>This OTP is valid for 30 minutes.</p>
                    <p>If you didn't request this verification email, please ignore it.</p>
                    <p>Best regards,<br>Paysofter Inc.</p>
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
                print('\nOTP resent:', email_otp.email_otp)
            except ApiException as e:
                print(e)
            return Response({'detail': 'Email verification OTP sent successfully.'}, status=status.HTTP_200_OK)
        except EmailOtp.DoesNotExist:
            return Response({'detail': 'User not found. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
