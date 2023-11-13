# payout/tasks.py
import random
import string

# from celery import Celery
from celery import shared_task
from django.db.models import Sum

from transaction.models import Transaction
from payout.models import Payout

def generate_payout_id():
    return ''.join(random.choices(string.digits, k=10)) 


@shared_task
def process_payouts():
    print("\nPayout processing starteed!")
    # Query transactions that are eligible for payout
    transactions_to_payout = Transaction.objects.filter(is_approved=True, payout_status=False)
    print(f"\nEligible transactions count: {len(transactions_to_payout)}")

    if transactions_to_payout:
        # Calculate the total amount to be paid out
        total_amount = transactions_to_payout.aggregate(Sum('amount'))['amount__sum']

        # Create payout records for each transaction
        for transaction in transactions_to_payout:
            payout = Payout.objects.create(
                seller=transaction.seller,
                transaction=transaction,
                amount=transaction.amount,
                # amount=total_amount, 
                currency=transaction.currency,
                payment_method=transaction.payment_method,
                is_approved=True,
                is_paid=True,
                payout_status=True,
                payout_id=generate_payout_id(),  
                payment_provider=transaction.payment_provider,
            )
            print(f"\nThe payout(s) created: {payout}")

        # Update the transaction payout_status
        transactions_to_payout.update(payout_status=True)

        # Implement the code to transfer funds to sellers here
        # You may use payment gateways or other methods to transfer funds

    return f"{len(transactions_to_payout)} transactions processed successfully" 


 
@shared_task
def process_promise_tansactions():
    print("\nPayout processing starteed!")





"""
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info
"""
