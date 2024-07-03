# fund_account/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('fund-user-account/', views.fund_user_account_view,
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

    path('debit-user-account-balance/', views.debit_user_fund_account,
         name='debit-user-account-balance'),
    path('debit-user-usd-account-fund/', views.debit_user_usd_account_fund,
         name='debit_user_usd_account_fund'),

    path('verify-otp/', views.verify_account_debit_email_otp, name='verify-otp'),
    path('verify-usd-account-debit-email-otp/', views.verify_usd_account_debit_email_otp,
         name='verify_usd_account_debit_email_otp'),



    # path('verify-ngn-fund-debit-otp/', views.verify_ngn_fund_debit_otp, name='verify-ngn-fund-debit-otp'),
    # path('verify-usd-fund-debit-otp/', views.verify_usd_fund_debit_otp, name='verify-usd-fund-debit-otp'),
    # path('verify-ngn-promise-debit-otp/', views.verify_ngn-promise_debit_otp, name='verify-ngn-promise-debit-otp'),
    # path('verify-usd-promise-debit-otp/', views.verify_usd_promise_debit_otp, name='verify-usd-promise-debit-otp'),

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
