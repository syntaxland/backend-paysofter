# transaction/urls.py
from django.urls import path
from . import views

urlpatterns = [  
    path('trigger-payout/', views.trigger_payout_process, name='trigger-payout'),
    path('get-user-payouts/', views.get_user_payouts, name='get-user-payouts'),
    # path('get-user-payouts/', views.GetUserPayouts.as_view(), name='get-user-payouts'),


]
