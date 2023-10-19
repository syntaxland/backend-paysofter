# payment/tasks.py
import random
import string

from decimal import Decimal

from celery import shared_task

from commission.models import Commission
from payout.models import Payout
from .models import PayoutPayment
from credit_point.models import CreditPointBalance, CreditPointEarning

from django.db.models import Sum
from django.contrib.auth import get_user_model

User = get_user_model() 


def generate_payout_payment_id():
    return ''.join(random.choices(string.digits, k=10)) 


def generate_commission_id():
    return ''.join(random.choices(string.digits, k=10)) 


@shared_task
def seller_payout_payment():
    print("\nCreating payout payments...")
    
    # Query Payout instances where is_approved, is_paid, and payout_status are all True
    payouts_to_create = Payout.objects.filter(is_paid=False, payout_status=True)

    for seller in payouts_to_create.values('seller').distinct():
        seller_id = seller['seller']
        
        # Calculate the total amount for the seller
        total_amount = payouts_to_create.filter(seller_id=seller_id).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

        # Calculate the commission (1% of the total amount)
        commission_percentage = Decimal('0.01')
        commission_amount = total_amount * commission_percentage

        # Deduct the commission from the total amount
        total_amount_after_commission = total_amount - commission_amount

        # Calculate the credit points earned 
        credit_points_earned = Decimal(str(commission_amount)) * Decimal('0.01')
        # referral_credit_points_bonus = Decimal(str(commission_amount)) * Decimal('0.005')
        
        try:
            # Get or create the user's credit point balance
            seller_user = User.objects.get(id=seller_id)
            credit_point, created = CreditPointBalance.objects.get_or_create( 
                user=seller_user,
                )
            
            credit_point.balance += credit_points_earned
            credit_point.save()
            print('Credit points added.')

            try:
                CreditPointEarning.objects.create(
                user=seller_user,
                credit_points_earned=credit_points_earned, 
                )
            except CreditPointEarning.DoesNotExist:
                pass
        except CreditPointBalance.DoesNotExist:
                pass
        
        # Create a PayoutPayment instance for the seller
        payout_payment = PayoutPayment.objects.create(
            seller=seller_user,
            total_amount=total_amount_after_commission,
            currency='NGN',  
            payment_method='Bank Transfer',  
            is_paid=False,  
            payout_payment_id=generate_payout_payment_id(), 
        )
        
        # You can add additional fields like bank_name, account_name, and bank_account_number
        # based on your requirements
        payouts_to_create.update(is_paid=True)

        # Save the PayoutPayment instance
        payout_payment.save()

        # Create a Commission instance to save the commission details
        commission = Commission.objects.create(
            payout_payment=payout_payment,
            commission_amount=commission_amount,
            commission_percentage=commission_percentage,
            currency='NGN', 
            payment_method='Commission Deduction',  
            status='success', 
            is_paid=True, 
            commission_id=generate_commission_id(),  
        )
        
        
        commission.save()
    return f"{len(payouts_to_create)} seller payout payments processed successfully" 



 
"""
celery -A core.celery worker --pool=solo -l info 
(Windows)
celery -A core.celery worker --loglevel=info (Unix) 
celery -A core.celery beat --loglevel=info 
"""
