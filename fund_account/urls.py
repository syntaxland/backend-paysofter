# fund_account/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('fund-user-account/', views.fund_user_account_view, name='fund-user-account'),
    path('get-user-acount-balance/', views.get_user_account_fund_balance, name='get-user-acount-balance'),
    path('user-account-funds/', views.get_user_account_funds, name='user-account-funds'),
    path('debit-user-account-balance/', views.debit_user_fund_account, name='debit-user-account-balance'),
    path('get-user-account-debits/', views.get_user_account_debits, name='get-user-account-debits'),

    path('toggle-activate-account/', views.toggle_is_account_active, name='toggle-activate-account'),
    path('set-maximum-withdrawal/', views.set_maximum_fund_withdrawal, name='set-maximum-withdrawal'),
    path('verify-otp/', views.verify_account_debit_email_otp, name='verify-otp'),
    path('send-otp-account-disable/', views.send_otp_account_fund_disable, name='send-otp-account-fund-disable'),
    path('verify-account-fund-disable/', views.verify_otp_account_fund_disable, name='verify-account-fund-disable'),
]
  