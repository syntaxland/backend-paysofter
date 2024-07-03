# payment/views.py
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import PayoutPayment
from .serializers import PaymentSerializer

from django.conf import settings
from django.http.response import HttpResponse
from .tasks import seller_payout_payment
from django.contrib.auth import get_user_model

User = get_user_model() 

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
