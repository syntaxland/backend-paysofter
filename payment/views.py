# payment/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from .models import PayoutPayment, PaymentLink
from .serializers import PaymentSerializer, PaymentLinkSerializer
from transaction.models import Transaction, TransactionCreditCard
from sellers.models import SellerAccount

from io import BytesIO
from PIL import Image, ImageDraw
import qrcode

from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
from django.http.response import HttpResponse
from .tasks import seller_payout_payment
from django.contrib.auth import get_user_model

User = get_user_model() 
  

# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# @parser_classes([MultiPartParser, FormParser])
# def create_payment_link(request):
#     user = request.user
#     data = request.data
#     serializer = PaymentLinkSerializer(data=data)

#     if serializer.is_valid():
#         payment = serializer.save(seller=user)
#         url = settings.PAYSOFTER_URL
#         link = f"{url}/link?ref={user.username}&pk={payment.pk}"
#         payment.payment_link = link

#         if 'payment_image' in request.FILES:
#             image = request.FILES['payment_image']
#             img = Image.open(image)
#             img.thumbnail((200, 200))  
#             img_io = BytesIO()
#             img.save(img_io, format=img.format)
#             img_io.seek(0)
#             thumbnail_image = ContentFile(img_io.getvalue(), name=image.name)
#             payment.payment_image.save(image.name, thumbnail_image, save=False)

#         qr = qrcode.QRCode(version=1, box_size=10, border=5)
#         qr.add_data(link)
#         qr.make(fit=True)

#         img = qr.make_image(fill='black', back_color='white')
#         blob = BytesIO()
#         img.save(blob, 'PNG') 
#         blob.seek(0) 
#         payment.payment_qrcode.save(f'{payment.pk}_qr.png', File(blob), save=False)

#         payment.save()
#         return Response({'success': 'Payment link created successfully.'}, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def create_payment_link(request):
    user = request.user
    data = request.data
    serializer = PaymentLinkSerializer(data=data)

    if serializer.is_valid():
        payment = serializer.save(seller=user)
        url = settings.PAYSOFTER_URL
        link = f"{url}/link?ref={user.username}&pk={payment.pk}"
        payment.payment_link = link
 
        # Generate the QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(link)
        qr.make(fit=True)

        img = qr.make_image(fill='black', back_color='white')
        blob = BytesIO()
        img.save(blob, 'PNG')
        payment.payment_qrcode.save(f'{payment.pk}_qr.png', File(blob), save=False)

        payment.save()
        return Response({'success': 'Payment link created successfully.'}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
@parser_classes([MultiPartParser, FormParser])
def get_payment_link_detail(request):
    link_id = request.GET.get('link_id', '')
    seller_username = request.GET.get('seller_username', '')
    print('link_id:', link_id, seller_username)

    seller = User.objects.get(username=seller_username) 
    print('seller:', seller)

    try:
        payment_link = PaymentLink.objects.get(seller=seller, id=link_id)
        serializer = PaymentLinkSerializer(payment_link)

        try:
            seller_account = SellerAccount.objects.get(seller=seller)
            seller_business_name = seller_account.business_name
            seller_trading_name = seller_account.trading_name
            seller_logo = seller_account.business_logo.url
            seller_test_api_key = seller.test_api_key
            seller_live_api_key = seller.live_api_key
            is_seller_api_key_live = seller.is_api_key_live
        except SellerAccount.DoesNotExist:
            seller_business_name = None
            seller_trading_name = None
            seller_logo = None
            seller_test_api_key = None
            seller_live_api_key = None
            is_seller_api_key_live = None
        print('is_seller_api_key_live:', is_seller_api_key_live)

        return Response({'data': serializer.data,
                         'seller_business_name': seller_business_name,
                         'seller_trading_name': seller_trading_name,
                         'seller_logo': seller_logo,
                         'seller_test_api_key': seller_test_api_key,
                         'seller_live_api_key': seller_live_api_key,
                         'is_seller_api_key_live': is_seller_api_key_live,
                         },
                        status=status.HTTP_200_OK)
    except PaymentLink.DoesNotExist:
        return Response({'detail': 'Payment link not found'}, status=status.HTTP_404_NOT_FOUND) 
    

@api_view(['PUT'])
@permission_classes([IsAuthenticated]) 
@parser_classes([MultiPartParser, FormParser])
def update_payment_link(request):
    user = request.user
    data = request.data
    link_id = data.get('link_id')
    print('link_id:', link_id)
 
    try:
        payment_link = PaymentLink.objects.get(seller=user, id=link_id)
    except PaymentLink.DoesNotExist:
        return Response({'detail': 'Link not found'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PaymentLinkSerializer(payment_link, data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({'detail': 'Link updated successfully.'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_payment_link(request):
    user = request.user
    data = request.data
    pk = data.get('pk')
    print('data:', data)
    
    try:
        ad = PaymentLink.objects.get(seller=user, id=pk)
        ad.delete()
        return Response({'detail': 'Link deleted successfully.'}) 
    except PaymentLink.DoesNotExist:
        return Response({'detail': 'Link not found.'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_seller_payment_links(request):
    try:
        user = request.user
        print(user)
        payment_link = PaymentLink.objects.filter(
            seller=user).order_by('-timestamp')
        serializer = PaymentLinkSerializer(payment_link, many=True)
        return Response(serializer.data)
    except PaymentLink.DoesNotExist:
        return Response({'detail': 'Payment Links not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated]) 
def create_payment(request):
    serializer = PaymentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_payments(request):
    payments = PayoutPayment.objects.filter(user=request.user)
    serializer = PaymentSerializer(payments, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


def trigger_seller_payout_payment(request):
    if seller_payout_payment:
        result = seller_payout_payment.delay()
        return HttpResponse({'task_id': result.id})
    return HttpResponse({'message': 'Invalid request method'})


class PaymentDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        paystack_public_key = settings.PAYSTACK_PUBLIC_KEY
        paysofter_public_key = settings.PAYSOFTER_PUBLIC_KEY

        return Response({
            "paystackPublicKey": paystack_public_key,
            "paysofterPublicKey": paysofter_public_key,
        })
