# fund_account/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('fund-user-account/', views.fund_user_account,
         name='fund-user-account'),
    path('get-user-acount-balance/', views.get_user_account_fund_balance,
         name='get-user-acount-balance'),
    path('get-all-account-fund-balance/', views.get_all_account_fund_balance,
         name='get-all-account-fund-balance'),

    path('user-account-funds/', views.get_user_account_funds,
         name='user-account-funds'),

    path('get-user-account-fund-debits/', views.get_user_account_funds_debits,
         name='get-user-account-fund-debits'),
    path('get-user-account-fund-credits/', views.get_user_account_funds_credits,
         name='uget-user-account-fund-credits'),

    path('get-user-account-debits/', views.get_user_account_debits,
         name='get-user-account-debits'),

    path('toggle-activate-account/', views.toggle_is_account_active,
         name='toggle-activate-account'),
    path('set-maximum-withdrawal/', views.set_maximum_fund_withdrawal,
         name='set-maximum-withdrawal'),
    path('set-maximum-usd-withdrawal/', views.set_maximum_usd_fund_withdrawal,
         name='set-maximum-usd-withdrawal'),

    path('send-debit-fund-account-otp/', views.send_debit_fund_account_otp,
         name='send_debit_fund_account_otp'),
    path('verify-otp/', views.verify_debit_fund_email_otp, name='verify_debit_fund_email_otp'),

    path('send-otp-account-disable/', views.send_otp_account_fund_disable,
         name='send-otp-account-fund-disable'),
    path('verify-account-fund-disable/', views.verify_otp_account_fund_disable,
         name='verify-account-fund-disable'),
    path('activate-account-fund/', views.activate_account_fund,
         name='activate-account-fund'),
    # path('enable-account-fund/', views.enable_account_fund, name='enable-account-fund'),

    path('toggle-usd-account/', views.toggle_is_usd_account_active,
         name='toggle-usd-account'),
    path('get-user-usd-account_fund-balance/', views.get_user_usd_account_fund_balance,
         name='get_user_usd_account_fund_balance'),
    path('fund-user-usd-account/', views.fund_user_usd_account,
         name='fund_user_usd_account'),


    path('get-user-usd-account-fund-credits/', views.get_user_usd_account_fund_credits,
         name='get_user_usd_account_fund_credits'),
    path('get-user-usd-account-fund-debits/',
         views.get_user_usd_account_debits, name='get_user_usd_account_debits'),
    path('set-usd-maximum-fund-withdrawal/', views.set_usd_maximum_fund_withdrawal,
         name='set-usd-maximum-fund-withdrawal'),
]
