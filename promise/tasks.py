# promise/tasks.py
import random
import string
# from celery import Celery 
from celery import shared_task
from decimal import Decimal 
from django.db.models import Sum
from django.db.utils import IntegrityError
from django.conf import settings

from send_email.send_email_sendinblue import send_email_sendinblue
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
                    is_approved=True,
                    payout_status=False,
                    is_success=promise.is_success,
                    transaction_id=promise.promise_id,
                    payment_method=promise.payment_method,
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

        # send_fund_seller_credit_alert_email(request, amount, currency, seller_email, debit_account_id, 
        #                         buyer_email, buyer_name, formatted_buyer_account_id, old_bal, new_bal, created_at)

    return f"{len(fulfilled_promises)} promise transactions processed successfully"


# def send_fund_seller_credit_alert_email(request, amount, currency, seller_email, debit_account_id, 
#                                 buyer_email, buyer_name, formatted_buyer_account_id, old_bal, new_bal, created_at):
#     print("Sending debit alert email...")
#     try:
#         subject = f"Paysofter Account Fund Debit Alert of {amount} {currency} with Debit Fund ID [{debit_account_id}]"
#         html_content = f"""
#                 <!DOCTYPE html>
#                 <html>
#                 <head>
#                     <title>Paysofter Account Fund Debit Alert</title>
#                     <style>
#                         body {{
#                             font-family: Arial, sans-serif;
#                             line-height: 1.6;
#                             color: #333;
#                         }}
#                         .container {{
#                             max-width: 600px;
#                             margin: 0 auto;
#                         }}
#                         .header {{
#                             background-color: #FF0000;
#                             color: white;
#                             padding: 1em;
#                             text-align: center;
#                         }}
#                         .content {{
#                             padding: 1em;
#                         }}
#                         .footer {{
#                             background-color: #f1f1f1;
#                             padding: 1em;
#                             text-align: center;
#                         }}
#                         .button {{
#                             display: inline-block;
#                             background-color: #e53935; /* Red background color */
#                             color: #fff;
#                             padding: 10px 20px;
#                             text-decoration: none;
#                             border-radius: 5px; /* Rounded corners */
#                         }}
#                         .summary-table {{
#                             width: 100%;
#                             border-collapse: collapse;
#                             margin: 20px 0;
#                         }}
#                         .summary-table th, .summary-table td {{
#                             border: 1px solid #ddd;
#                             padding: 8px;
#                             text-align: left;
#                         }}
#                         .summary-table th {{
#                             background-color: #f2f2f2;
#                         }}
#                     </style>
#                 </head>
#                 <body>
#                     <div class="container">
#                         <div class="header">
#                             <h2>Paysofter Account Fund Debit Alert</h2>
#                         </div>
#                         <div class="content">
#                             <p>Dear {buyer_name.title()},</p>
#                             <p>This is to inform you that your Paysofter Account Fund with account ID: ({formatted_buyer_account_id}) 
#                             has been debited with 
#                             <strong>{amount} {currency}</strong> being payment made to <b>{seller_email}</b> with a <b>Debit Fund ID: 
#                             "{debit_account_id}"</b> at <b>{created_at}</b>.</p>
#                             <table class="summary-table">
#                                 <tr>
#                                     <th>Detail</th>
#                                     <th>Information</th>
#                                 </tr>
#                                 <tr>
#                                     <td>Amount</td>
#                                     <td>{amount} {currency}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Debit Fund ID</td>
#                                     <td>{debit_account_id}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Seller Email</td>
#                                     <td>{seller_email}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Buyer Account ID</td>
#                                     <td>{formatted_buyer_account_id}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Old Bal</td>
#                                     <td>{old_bal}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>New Bal</td>
#                                     <td>{new_bal}</td>
#                                 </tr>
#                                 <tr>
#                                     <td>Date and Time</td>
#                                     <td>{created_at}</td>
#                                 </tr>
#                             </table>
#                             <p>If you have received this email in error, please ignore it.</p>
#                             <p>Best regards,</p>
#                             <p>Paysofter Inc.</p>
#                         </div>
#                         <div class="footer">
#                             <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
#                             <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
#                         </div>
#                     </div>
#                 </body>
#                 </html>
#             """
#         html_content = html_content
#         subject = subject
#         to = [{"email": buyer_email, "name": buyer_name}]
#         send_email_sendinblue(subject, html_content, to)
#     except Exception as e:
#         print(e)
#         return {'detail': str(e), 'status': 500}


"""
redis-server 
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info 
"""
