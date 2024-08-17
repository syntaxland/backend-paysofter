# sellers/views.py 
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from .models import (SellerAccount, BusinessOwnerDetail,  
                     BankAccount, BankVerificationNumber, 
                     SellerPhoto, BusinessStatus)
from .serializers import (SellerAccountSerializer, 
                          BusinessOwnerDetailSerializer, 
                          SellerPhotoSerializer, BankAccountSerializer, 
                          BankVerificationNumberSerializer, 
                          BusinessStatusSerializer)

from django.contrib.auth import get_user_model

User = get_user_model()

 
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
