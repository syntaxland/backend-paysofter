# payout/tasks.py
import random
import string
from decimal import Decimal
# from celery import Celery
from celery import shared_task
from django.db.models import Sum
from django.conf import settings

from send_email.send_email_sendinblue import send_email_sendinblue
from transaction.models import Transaction
from payout.models import Payout
from promise.models import PaysofterPromise
from fund_account.models import (
                     AccountFundBalance,
                     UsdAccountFundBalance,
                     )

def generate_payout_id():
    return ''.join(random.choices(string.digits, k=20)) 


def generate_payout_id():
    letters_and_digits = string.ascii_uppercase + string.digits
    return 'PYO'+''.join(random.choices(letters_and_digits, k=17))


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
def process_promise_bank_payouts():
    print("\nbank Payout processing starteed!")


# @shared_task
def get_seller_promise_sum_fund_payouts():
    print("\nFund Payout processing starteed!")


@shared_task
def process_promise_fund_payouts():
    print("\nFund Payout processing started!")

    # Query promises that are fulfilled by buyers and not delivered yet
    fulfilled_promises = PaysofterPromise.objects.filter(
        buyer_promise_fulfilled=True,
        is_delivered=False,
        seller__seller_payout_choice='Paysofter Account Fund'
    )
    print(f"\nFulfilled promises count: {len(fulfilled_promises)}")

    if fulfilled_promises:
        for promise in fulfilled_promises:
            # Deduct 2% if is_settle_conflict_activated is True
            amount = promise.amount
            settle_conflict_charges = 0  # Initialize settle_conflict_charges

            if promise.is_settle_conflict_activated:
                settle_conflict_charges = Decimal(amount) * Decimal(0.02)  # Deduct 2%

            # Calculate the net amount to be credited
            net_amount = Decimal(amount) - Decimal(settle_conflict_charges)

            user = promise.seller

            # Check the currency and update the respective fund balance
            if promise.currency == "NGN":
                fund_balance, created = AccountFundBalance.objects.get_or_create(user=user)
            elif promise.currency == "USD":
                fund_balance, created = UsdAccountFundBalance.objects.get_or_create(user=user)
            else:
                print(f"Unsupported currency: {promise.currency} for user: {user}")
                continue

            old_bal = fund_balance.balance
            new_bal = old_bal + net_amount

            # Update the fund balance
            fund_balance.balance = new_bal
            fund_balance.save()

            # Generate payout ID
            payout_id = generate_payout_id()

            # Send credit alert email
            send_fund_seller_credit_alert_email(
                request=None,
                amount=net_amount,
                currency=promise.currency,
                seller_email=user.email,
                credit_fund_id=payout_id,
                seller_name=user.username,
                formatted_buyer_account_id=user.account_id,
                old_bal=old_bal,
                new_bal=new_bal,
                created_at=promise.timestamp
            )

        # Update is_delivered for all fulfilled promises
        fulfilled_promises.update(is_delivered=True)

    return f"{len(fulfilled_promises)} promise transactions processed successfully"


def send_fund_seller_credit_alert_email(request, amount, currency, seller_email, credit_fund_id, 
                                seller_name, formatted_buyer_account_id, old_bal, new_bal, created_at):
    print("Sending debit alert email...")
    try:
        subject = f"Paysofter Account Fund Credit Alert of {amount} {currency} with Credit Fund ID [{credit_fund_id}]"
        html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Paysofter Account Fund Debit Alert</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            line-height: 1.6;
                            color: #333;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        .header {{
                            background-color: #FF0000;
                            color: white;
                            padding: 1em;
                            text-align: center;
                        }}
                        .content {{
                            padding: 1em;
                        }}
                        .footer {{
                            background-color: #f1f1f1;
                            padding: 1em;
                            text-align: center;
                        }}
                        .button {{
                            display: inline-block;
                            background-color: #e53935; /* Red background color */
                            color: #fff;
                            padding: 10px 20px;
                            text-decoration: none;
                            border-radius: 5px; /* Rounded corners */
                        }}
                        .summary-table {{
                            width: 100%;
                            border-collapse: collapse;
                            margin: 20px 0;
                        }}
                        .summary-table th, .summary-table td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: left;
                        }}
                        .summary-table th {{
                            background-color: #f2f2f2;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h2>Paysofter Account Fund Debit Alert</h2>
                        </div>
                        <div class="content">
                            <p>Dear {seller_name.title()},</p>
                            <p>This is to inform you that your Paysofter Account Fund with account ID: ({formatted_buyer_account_id}) 
                            has been credited with 
                            <strong>{amount} {currency}</strong> being a payout with a <b>Fund ID: 
                            "{credit_fund_id}"</b> at <b>{created_at}</b>.</p>
                            <table class="summary-table">
                                <tr>
                                    <th>Detail</th>
                                    <th>Information</th>
                                </tr>
                                <tr>
                                    <td>Amount</td>
                                    <td>{amount} {currency}</td>
                                </tr>
                                <tr>
                                    <td>Debit Fund ID</td>
                                    <td>{credit_fund_id}</td>
                                </tr>
                                <tr>
                                    <td>Seller Email</td>
                                    <td>{seller_email}</td>
                                </tr>
                                
                                <tr>
                                    <td>Old Bal</td>
                                    <td>{old_bal}</td>
                                </tr>
                                <tr>
                                    <td>New Bal</td>
                                    <td>{new_bal}</td>
                                </tr>
                                <tr>
                                    <td>Date and Time</td>
                                    <td>{created_at}</td>
                                </tr>
                            </table>
                            <p>If you have received this email in error, please ignore it.</p>
                            <p>Best regards,</p>
                            <p>Paysofter Inc.</p>
                        </div>
                        <div class="footer">
                            <p><em>If you have any issue with this payment, kindly reply this email or send email to: <b>{seller_email}</b></em></p>
                            <p><em>{settings.COMPANY_NAME} is a subsidiary and registered trademark of {settings.PARENT_COMPANY_NAME}.</em></p>
                        </div>
                    </div>
                </body>
                </html>
            """
        html_content = html_content
        subject = subject
        to = [{"email": seller_email}]
        send_email_sendinblue(subject, html_content, to)
    except Exception as e:
        print(e)
        return {'detail': str(e), 'status': 500}


"""
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info
"""
