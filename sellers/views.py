# sellers/views.py 
import random
import string
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (SellerAccount, BusinessOwnerDetail,  
                     BankAccount, BankVerificationNumber, 
                     SellerPhoto, BusinessStatus, UsdBankAccount)
from .serializers import (SellerAccountSerializer, 
                          BusinessOwnerDetailSerializer, 
                          SellerPhotoSerializer, BankAccountSerializer, 
                          BankVerificationNumberSerializer, 
                          BusinessStatusSerializer, UsdBankAccountSerializer)

from user_profile.serializers import UserProfileSerializer
                     
from django.contrib.auth import get_user_model

User = get_user_model()


def generate_seller_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'SID'+''.join(random.choices(letters_and_digits, k=7))

 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_seller_account(request):
    seller_account, created = SellerAccount.objects.get_or_create(seller=request.user)
    serializer = SellerAccountSerializer(instance=seller_account, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST']) 
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_business_status(request):
    business_status, created = BusinessStatus.objects.get_or_create(seller=request.user)
    serializer = BusinessStatusSerializer(instance=business_status, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def business_owner_detail(request):
    business_owner_detail, created = BusinessOwnerDetail.objects.get_or_create(seller=request.user)
    serializer = BusinessOwnerDetailSerializer(instance=business_owner_detail, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_seller_bank_account(request):
    bank_account, created = BankAccount.objects.get_or_create(seller=request.user)
    serializer = BankAccountSerializer(instance=bank_account, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_seller_bvn(request):
    bvn, created = BankVerificationNumber.objects.get_or_create(seller=request.user)
    serializer = BankVerificationNumberSerializer(instance=bvn, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_seller_photo(request):
    seller=request.user
    data=request.data
    print('seller:', seller)
    print('data:', data)
    photo, created = SellerPhoto.objects.get_or_create(seller=seller)
    serializer = SellerPhotoSerializer(instance=photo, data=data)
    
    if serializer.is_valid():
        serializer.save()

        seller.is_seller = True
        seller.save() 

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_account(request):
    user = request.user
    try:
        seller_account = SellerAccount.objects.get(seller=user)
        serializer = SellerAccountSerializer(seller_account)
        return Response(serializer.data)
    except SellerAccount.DoesNotExist:
        return Response({'detail': 'Seller account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_seller_account(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        seller_account = SellerAccount.objects.get(seller=user)
    except SellerAccount.DoesNotExist:
        return Response({'detail': 'Seller account not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = SellerAccountSerializer(seller_account, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Seller account updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def get_business_status(request):
    user = request.user
    try:
        business_status = BusinessStatus.objects.get(seller=user)
        serializer = BusinessStatusSerializer(business_status)
        return Response(serializer.data)
    except BusinessStatus.DoesNotExist:
        return Response({'detail': 'Business status not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_business_status(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        business_status = BusinessStatus.objects.get(seller=user)
    except BusinessStatus.DoesNotExist:
        return Response({'detail': 'Business status not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BusinessStatusSerializer(business_status, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Business status updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def get_business_owner_details(request):
    user = request.user
    try:
        business_owner_detail = BusinessOwnerDetail.objects.get(seller=user)
        serializer = BusinessOwnerDetailSerializer(business_owner_detail)
        return Response(serializer.data)
    except BusinessOwnerDetail.DoesNotExist:
        return Response({'detail': 'Seller details not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_business_owner_details(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        business_owner_detail = BusinessOwnerDetail.objects.get(seller=user)
    except BusinessOwnerDetail.DoesNotExist:
        return Response({'detail': 'Seller details not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BusinessOwnerDetailSerializer(business_owner_detail, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Seller details updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_bank_account(request):
    user = request.user
    try:
        seller_account = BankAccount.objects.get(seller=user)
        serializer = BankAccountSerializer(seller_account)
        return Response(serializer.data)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Seller bank account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_seller_bank_account(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        seller_account = BankAccount.objects.get(seller=user)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Seller bank account not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BankAccountSerializer(seller_account, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Seller bank account updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_bvn(request):
    user = request.user
    try:
        seller_bvn = BankVerificationNumber.objects.get(seller=user)
        serializer = BankVerificationNumberSerializer(seller_bvn)
        return Response(serializer.data)
    except BankVerificationNumber.DoesNotExist:
        return Response({'detail': 'Seller bvn not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_seller_bvn(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        seller_bvn = BankVerificationNumber.objects.get(seller=user)
    except BankVerificationNumber.DoesNotExist:
        return Response({'detail': 'Seller bvn not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = BankVerificationNumberSerializer(seller_bvn, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Seller bvn updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def get_seller_photo(request):
    user = request.user
    try:
        seller_photo = SellerPhoto.objects.get(seller=user)
        serializer = SellerPhotoSerializer(seller_photo)
        return Response(serializer.data)
    except SellerPhoto.DoesNotExist:
        return Response({'detail': 'Seller photo not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_seller_photo(request):
    user = request.user
    data = request.data
    print('data:', data)
    try:
        seller_photo = SellerPhoto.objects.get(seller=user)
    except SellerPhoto.DoesNotExist:
        return Response({'detail': 'Seller photo not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = SellerPhotoSerializer(seller_photo, data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Seller photo updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def get_all_sellers_account(request):
    user = request.user
    try:
        seller_account = SellerAccount.objects.all()
        serializer = SellerAccountSerializer(seller_account)
        return Response(serializer.data)
    except SellerAccount.DoesNotExist:
        return Response({'detail': 'Seller account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def get_all_business_status(request):
    user = request.user
    try:
        business_status = BusinessStatus.objects.all()
        serializer = BusinessStatusSerializer(business_status)
        return Response(serializer.data)
    except BusinessStatus.DoesNotExist:
        return Response({'detail': 'Business status not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def get_all_business_owners_details(request):
    user = request.user
    try:
        business_owner_detail = BusinessOwnerDetail.objects.all()
        serializer = BusinessOwnerDetailSerializer(business_owner_detail)
        return Response(serializer.data)
    except BusinessOwnerDetail.DoesNotExist:
        return Response({'detail': 'Seller details not found'}, status=status.HTTP_404_NOT_FOUND)       


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def get_all_sellers_bvn(request):
    user = request.user
    try:
        seller_bvn = BankVerificationNumber.objects.all()
        serializer = BankVerificationNumberSerializer(seller_bvn)
        return Response(serializer.data)
    except BankVerificationNumber.DoesNotExist:
        return Response({'detail': 'Seller bvn not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
@parser_classes([MultiPartParser, FormParser])
def get_all_seller_photo(request):
    user = request.user
    try:
        seller_photo = SellerPhoto.objects.all()
        serializer = SellerPhotoSerializer(seller_photo)
        return Response(serializer.data)
    except SellerPhoto.DoesNotExist:
        return Response({'detail': 'Seller photo not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def get_all_sellers_bank_account(request):
    user = request.user
    try:
        seller_account = BankAccount.objects.all()
        serializer = BankAccountSerializer(seller_account)
        return Response(serializer.data)
    except BankAccount.DoesNotExist:
        return Response({'detail': 'Seller bank account not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def get_all_sellers(request):
    try:
        sellers = User.objects.filter(is_seller=True)
        serializer = UserProfileSerializer(sellers, many=True)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({'detail': 'Sellers not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@permission_classes([IsAdminUser])
def get_seller_account_detail(request, seller_username):
    seller = User.objects.get(username=seller_username) 
    print('seller_username:', seller_username)
    print('seller:', seller)
 
    try:
        seller_account_serializer = None
        business_status_serializer = None
        business_owners_details_serializer = None
        seller_ngn_bank_serializer = None
        seller_usd_bank_serializer = None 
        seller_bvn_serializer = None
        seller_photo_url = None

        seller_account = SellerAccount.objects.get(seller=seller)
        seller_account_serializer = SellerAccountSerializer(seller_account)

        try:
            business_status = BusinessStatus.objects.get(seller=seller)
            business_status_serializer = BusinessStatusSerializer(business_status)
        except BusinessStatus.DoesNotExist:
            business_status_serializer = None
            pass

        try:
            business_owners_details = BusinessOwnerDetail.objects.get(seller=seller)
            business_owners_details_serializer = BusinessOwnerDetailSerializer(business_owners_details)
        except BusinessOwnerDetail.DoesNotExist:
            business_owners_details_serializer = None
            pass

        try:
            seller_ngn_bank = BankAccount.objects.get(seller=seller)
            seller_ngn_bank_serializer = BankAccountSerializer(seller_ngn_bank)
        except BankAccount.DoesNotExist:
            seller_ngn_bank_serializer = None
            pass

        try:
            seller_usd_bank = UsdBankAccount.objects.get(seller=seller)
            seller_usd_bank_serializer = UsdBankAccountSerializer(seller_usd_bank)
        except UsdBankAccount.DoesNotExist:
            seller_usd_bank_serializer = None
            pass

        try:
            seller_bvn = BankVerificationNumber.objects.get(seller=seller)
            seller_bvn_serializer = BankVerificationNumberSerializer(seller_bvn)
        except BankVerificationNumber.DoesNotExist:
            seller_bvn_serializer = None
            pass

        try:
            seller_photo = SellerPhoto.objects.get(seller=seller)
            # seller_photo_serializer = SellerPhotoSerializer(seller_photo)
            seller_photo_url = seller_photo.photo.url
        except SellerPhoto.DoesNotExist:
            seller_photo_url = None
            pass
        
        print('data processed!')
        return Response({
            'seller_account': seller_account_serializer.data if seller_account_serializer else None,
            'business_status': business_status_serializer.data if business_status_serializer else None,
            'business_owners_details': business_owners_details_serializer.data if business_owners_details_serializer else None,
            'seller_ngn_bank': seller_ngn_bank_serializer.data if seller_ngn_bank_serializer else None,
            'seller_usd_bank': seller_usd_bank_serializer.data if seller_usd_bank_serializer else None,
            'seller_bvn': seller_bvn_serializer.data if seller_bvn_serializer else None,
            'seller_photo_url': seller_photo_url,
        }, status=status.HTTP_200_OK)
    except SellerAccount.DoesNotExist:
        return Response({'detail': 'Seller Account not found'}, status=status.HTTP_404_NOT_FOUND) 


@api_view(['POST'])
@permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def verify_seller(request):
    data = request.data
    user = request.user
    print('data:', data)

    seller_username = data.get('seller_username')
    password = data.get('password')

    if not user.check_password(password):
        return Response({'detail': 'Invalid password.'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        seller = User.objects.get(username=seller_username)
    except User.DoesNotExist:
        return Response({'detail': 'Seller fund not found.'}, status=status.HTTP_404_NOT_FOUND)

    seller_id = generate_seller_id()
    seller.seller_id = seller_id
    seller.is_seller_account_verified = True
    seller.save()
    print('seller_id:', seller.seller_id)

    return Response({'detail': f'Success!', }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_paysofter_account_id(request):
    seller_id = request.data.get('seller_id')
    print('seller_id:', seller_id)

    try:
        user = User.objects.get(seller_id=seller_id)
        account_id = user.account_id
        formatted_account_id = format_number(account_id)
    except User.DoesNotExist:
        return Response({'detail': f'Paysofter user with Seller ID: "{seller_id}" does not exist. Please try again.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': 'Success', 'account_id': account_id, 'formatted_account_id': formatted_account_id}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_paysofter_seller_id(request):
    security_code = request.data.get('security_code')
    print('security_code:', security_code)

    try:
        user = User.objects.get(security_code=security_code)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid or expired Security Code. Please refresh Security Code and try again.'}, status=status.HTTP_404_NOT_FOUND)
    return Response({'detail': f'Success!', }, status=status.HTTP_200_OK)


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
