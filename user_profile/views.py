# user_profile/views.py
import random
import string
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status, generics
from rest_framework.request import Request
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from rest_auth.registration.views import SocialLoginView 

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
# from rest_auth.registration.serializers import SocialLoginSerializer

# from .models import UserProfile
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserSerializerWithToken,
    MyTokenObtainPairSerializer,
    DeleteAccountSerializer, 
    ChangePasswordSerializer,
    UpdateUserProfileSerializer,
    AvatarUpdateSerializer,
    GoogleLoginSerializer
)

# from send_email_otp.serializers import EmailOTPSerializer
from referral.models import Referral
# from send_email_otp.models import EmailOtp

from django.core.exceptions import PermissionDenied
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_test_api_key():
    letters_and_digits = string.ascii_lowercase + string.digits
    return 'test_api_key_'+''.join(random.choices(letters_and_digits, k=50))

def generate_test_api_secret_key():
    letters_and_digits = string.ascii_lowercase + string.digits
    return 'test_api_secret_key_'+''.join(random.choices(letters_and_digits, k=50))

def generate_live_api_key():
    letters_and_digits = string.ascii_lowercase + string.digits
    return 'live_api_key_'+''.join(random.choices(letters_and_digits, k=50))

def generate_live_api_secret_key():
    letters_and_digits = string.ascii_lowercase + string.digits
    return 'live_api_secret_key_'+''.join(random.choices(letters_and_digits, k=50))

def generate_referral_code():
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choices(letters_and_digits, k=9))

def generate_account_id():
    return ''.join(random.choices(string.digits, k=12))


def generate_security_code():
    return ''.join(random.choices(string.digits, k=4))


@api_view(['POST'])
@permission_classes([AllowAny])
def user_register_view(request):
    data = request.data
    serializer = UserSerializer(data=data)

    email = data.get('email')
    phone_number = data.get('phone_number')

    try:
        user_with_email_not_verified = User.objects.get(email=email)
        if not user_with_email_not_verified.is_verified:
            return Response({'detail': 'A user with this email already exists but not verified. Login to verify your account.'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass

    try:
        user_with_email = User.objects.get(email=email) 
        if user_with_email.is_verified:
            return Response({'detail': 'A user with this email already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass
    
    try:
        user_with_phone = User.objects.get(phone_number=phone_number) 
        if user_with_phone.is_verified:
            return Response({'detail': 'A user with this phone number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
    except User.DoesNotExist:
        pass
     
    if serializer.is_valid():
        test_api_key = generate_test_api_key()
        test_api_secret_key = generate_test_api_secret_key()
        live_api_key = generate_live_api_key()
        live_api_secret_key = generate_live_api_secret_key()
        account_id = generate_account_id()
        security_code = generate_security_code()

        # User does not exist, create the user and send verification OTP
        print('\nCreating user...')
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            phone_number=data.get('phone_number'),
            password=data.get('password'),

            test_api_key=test_api_key,
            test_api_secret_key=test_api_secret_key,
            live_api_key=live_api_key,
            live_api_secret_key=live_api_secret_key,

            account_id=account_id,
            security_code=security_code,
        )

        try:
            url = settings.PAYSOFTER_URL
            print('url:', url)
            if not user.referral_code:
                user.referral_code = generate_referral_code()
                user.save()
            if not user.referral_link:
                referral_link =  f"{url}/register?ref={user.referral_code}" 
                # referral_link =  f"http://mcdofglobal.s3-website-us-east-1.amazonaws.com/register?ref={user.referral_code}"
                user.referral_link = referral_link
                user.save()
        except Exception as e:
            print(e)
                         
        referral_code = data.get('referral_code')
        print('referral_code:', referral_code)
        
        if referral_code:
            try:
                referrer = User.objects.get(referral_code=referral_code) 
                referral, created = Referral.objects.get_or_create(referrer=referrer)
                referral.referred_users.add(user)
                # referral.user_count += 1
                referrer.save()
                print('user added to referred_users of referrer:', user)
            except User.DoesNotExist:
                pass

            print('\nUser created! Verify your email.')
        if user.is_verified:
            return Response({'detail': 'User already exists. Please login.'}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'User created. Please verify your email.'}, status=status.HTTP_201_CREATED)
    else:
        print('Error creating user.')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class GoogleLogin(SocialLoginView):
    # permission_classes = [AllowAny]  
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
    serializer_class = GoogleLoginSerializer  
    # callback_url = "http://localhost:3000"
    # serializer_class = SocialLoginSerializer
    # serializer_class = MyTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=204)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)


class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        print(user)
        serializer = UserProfileSerializer(user)
        return Response(serializer.data)
    

class UpdateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UpdateUserProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'detail': 'Profile updated successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = AvatarUpdateSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Check if the user making the request matches the user being updated
            if user.id == serializer.validated_data.get('id'):
                # Handle avatar update here
                if 'avatar' in request.FILES:
                    user.avatar = request.FILES['avatar']
                user.save()
                
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied("You don't have permission to update this user.")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({'detail': 'Password changed successfully.'})
        else:
            return Response({'detail': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class AccountDeleteView(APIView): 
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DeleteAccountSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            password = serializer.validated_data['password']

            if user.check_password(password):
                user.delete()
                return Response({'detail': 'Account deleted successfully.'})
            else:
                return Response({'detail': 'Incorrect password.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
