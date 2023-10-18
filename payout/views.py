# payout/views.py
import random
import string

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http.response import HttpResponse
from rest_framework.views import APIView

from django.contrib.auth import get_user_model
from .serializers import PayoutSerializer
from .models import Payout
from transaction.models import Transaction
from payout.tasks import process_payouts

User = get_user_model()


def generate_payout_id():
    return ''.join(random.choices(string.digits, k=10))


def seller_payout(request):
    # Find transactions that haven't been paid out yet
    pending_transactions = Transaction.objects.filter(is_success=True, payout_status=False)
    for transaction in pending_transactions:
        # Calculate the amount to be paid out (you can add any logic here)
        amount_to_payout = transaction.amount 

        # Create a new Payout instance
        payout = Payout.objects.create(seller=transaction.seller, amount=amount_to_payout)

        # Mark the transaction as paid out
        transaction.payout = payout
        transaction.save()
    return Response({'message': 'Payout process initiated.'})


# @api_view(['POST'])
# def trigger_payout_process(request):
#     if request.method == 'POST':
#         result = process_payouts.delay()
#         return Response({'task_id': result.id})
#     return Response({'message': 'Invalid request method'}, status=status.HTTP_400_BAD_REQUEST)


def trigger_payout_process(request):
    if process_payouts:
        result = process_payouts.delay()
        return HttpResponse({'task_id': result.id})
    return HttpResponse({'message': 'Invalid request method'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_payouts(request):
    try:
        user = request.user
        print(user, type(user))
        # payouts = Payout.objects.all().order_by('-timestamp')
        payouts = Payout.objects.filter(seller=user).order_by('-timestamp')
        serializer = PayoutSerializer(payouts, many=True)
        return Response(serializer.data)
    except Payout.DoesNotExist:
            return Response({'detail': 'Payouts not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
# @permission_classes([IsAdminUser])
@permission_classes([IsAuthenticated])
def get_all_user_payouts(request):
    try:
        payouts = Payout.objects.all().order_by('-timestamp')
        serializer = PayoutSerializer(payouts, many=True)
        return Response(serializer.data)
    except Payout.DoesNotExist:
            return Response({'detail': 'Payouts not found'}, status=status.HTTP_404_NOT_FOUND)
