# promise/tasks.py
import random
import string
# from celery import Celery
from celery import shared_task
from decimal import Decimal
from django.db.models import Sum
from django.db.utils import IntegrityError

from promise.models import PaysofterPromise
from transaction.models import Transaction 


def generate_transaction_id():
    return ''.join(random.choices(string.digits, k=16)) 


# @shared_task
# def process_promise_transactions(): 
#     print("\nPromise transactions processing started!")

#     # Query promises that are fulfilled by buyers
#     fulfilled_promises = PaysofterPromise.objects.filter(
#         buyer_promise_fulfilled=True, 
#         is_delivered=False
#     )
#     print(f"\nFulfilled promises count: {len(fulfilled_promises)}")

#     if fulfilled_promises:
#         for promise in fulfilled_promises:
#             # Deduct 2% if is_settle_conflict_activated is True
#             amount = promise.amount
#             settle_conflict_charges = 0  # Initialize settle_conflict_charges

#             if promise.is_settle_conflict_activated:
#                 settle_conflict_charges = Decimal(amount) * Decimal(0.02)  # Deduct 2%

#             # Create a Transaction record for each fulfilled promise
#             transaction = Transaction.objects.create(
#                 seller=promise.seller,
#                 # buyer_email=promise.buyer.email,
#                 buyer_email=promise.buyer.email if promise.buyer else None,
#                 amount=amount,
#                 currency=promise.currency,
#                 payment_method=promise.payment_method,
#                 is_approved=True,
#                 payout_status=False,  
#                 is_success=promise.is_success,
#                 transaction_id=promise.promise_id,  
#                 payment_provider=promise.payment_provider,
#             )


#             print(f"\nThe transaction created: {transaction}")

#             # Update settle_conflict_charges in PaysofterPromise
#             promise.settle_conflict_charges = settle_conflict_charges
#             promise.save()

#         # Update is_delivered for all fulfilled promises
#         fulfilled_promises.update(is_delivered=True)

#         # transfer funds to sellers

#     return f"{len(fulfilled_promises)} promise transactions processed successfully"


@shared_task
def process_promise_transactions():
    print("\nPromise transactions processing started!")

    # Query promises that are fulfilled by buyers
    fulfilled_promises = PaysofterPromise.objects.filter(
        buyer_promise_fulfilled=True,
        is_delivered=False
    )
    print(f"\nFulfilled promises count: {len(fulfilled_promises)}")

    if fulfilled_promises:
        for promise in fulfilled_promises:
            # Deduct 2% if is_settle_conflict_activated is True
            amount = promise.amount
            settle_conflict_charges = 0  # Initialize settle_conflict_charges

            if promise.is_settle_conflict_activated:
                settle_conflict_charges = Decimal(amount) * Decimal(0.02)  # Deduct 2%

            # Check for existing transaction with the same promise_id
            if Transaction.objects.filter(transaction_id=promise.promise_id).exists():
                print(f"Transaction with ID {promise.promise_id} already exists. Skipping...")
                continue

            try:
                # Create a Transaction record for each fulfilled promise
                transaction = Transaction.objects.create(
                    seller=promise.seller,
                    buyer_email=promise.buyer.email if promise.buyer else None,
                    amount=amount,
                    currency=promise.currency,
                    payment_method=promise.payment_method,
                    is_approved=True,
                    payout_status=False,
                    is_success=promise.is_success,
                    transaction_id=promise.promise_id,
                    payment_provider=promise.payment_provider,
                )
                print(f"\nThe transaction created: {transaction}")

                # Update settle_conflict_charges in PaysofterPromise
                promise.settle_conflict_charges = settle_conflict_charges
                promise.save()

            except IntegrityError as e:
                print(f"\nIntegrityError: {e}")
                continue

        # Update is_delivered for all fulfilled promises
        fulfilled_promises.update(is_delivered=True)

        # Transfer funds to sellers

    return f"{len(fulfilled_promises)} promise transactions processed successfully"


"""
redis-server
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info 
"""
