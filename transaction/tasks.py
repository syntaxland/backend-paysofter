# transaction/tasks.py
import random
import string

# from celery import Celery
from celery import shared_task
from django.db.models import Sum

from promise.models import PaysofterPromise
from transaction.models import Transaction


def generate_transaction_id():
    return ''.join(random.choices(string.digits, k=10))  


# @shared_task
# def process_promise_transactions():
#     print("\nPromise transactions processing started!")

#     # Query promises that are fulfilled by buyers
#     fulfilled_promises = PaysofterPromise.objects.filter(buyer_promise_fulfilled=True)

#     print(f"\nFulfilled promises count: {len(fulfilled_promises)}")

#     if fulfilled_promises:
#         for promise in fulfilled_promises:
#             # Create a Transaction record for each fulfilled promise
#             transaction = Transaction.objects.create(
#                 seller=promise.seller,
#                 buyer_email=promise.buyer.email,
#                 amount=promise.amount,
#                 currency=promise.currency,
#                 payment_method=promise.payment_method,
#                 is_approved=True,
#                 payout_status=False,  # Assuming payout is done immediately after transaction
#                 is_success=promise.is_success,
#                 payment_id=promise.promise_id,  # Assuming promise_id can be used as payment_id
#                 transaction_id=generate_transaction_id(),  # You may generate a unique transaction_id
#                 payment_provider=promise.payment_provider,
#             )
#             print(f"\nThe transaction created: {transaction}")


#         # transfer funds to sellers

#     return f"{len(fulfilled_promises)} promise transactions processed successfully"





# """
# redis-server
# celery -A core.celery worker --pool=solo -l info 
# (Windows)
# celery -A core.celery worker --loglevel=info (Unix) 
# celery -A core.celery beat --loglevel=info
# """
