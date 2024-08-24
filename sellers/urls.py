# urls.py
from django.urls import path
from . import views

urlpatterns = [

    path('create-business-status/', views.create_business_status, name='create-business-status'),
    path('get-business-status/', views.get_business_status, name='get-business-status'),
    path('update-business-status/', views.update_business_status, name='update-business-status'),

    path('get-seller-account/', views.get_seller_account, name='get-seller-account'), 
    path('update-seller-account/', views.update_seller_account, name='update-seller-account'),

    path('get-business-owner-details/', views.get_business_owner_details, name='get-business-owner-details'),
    path('update-business-owner-details/', views.update_business_owner_details, name='update-business-owner-details'),

    path('get-seller-bank-account/', views.get_seller_bank_account, name='get-seller-bank-account'),
    path('update-seller-bank_account/', views.update_seller_bank_account, name='update-seller-bank-account'),

    path('get-seller-bvn/', views.get_seller_bvn, name='get-seller-bvn'),
    path('update-seller-bvn/', views.update_seller_bvn, name='update-seller-bvn'),

    path('get-seller-photo/', views.get_seller_photo, name='get-seller-photo'),
    path('update-seller-photo/', views.update_seller_photo, name='update-seller-photo'),

    path('create-seller-account/', views.create_seller_account, name='create-seller-account'), 
    path('business-owner-detail/', views.business_owner_detail, name='business-owner-detail'),
    path('create-seller-bank/', views.create_seller_bank_account, name='create-seller-bank'),
    path('create-seller-bvn/', views.create_seller_bvn, name='seller-bvn'),
    path('create-seller-photo/', views.create_seller_photo, name='seller-photo'),

    path('get-all-sellers-account/', views.get_all_sellers_account, name='get_all_sellers_account'),
    path('get-all-business-status/', views.get_all_business_status, name='get_all_business_status'),
    path('get-all-business-owners-details/', views.get_all_business_owners_details, name='get_all_business_owners_details'),
    path('get-all-sellers-bvn/', views.get_all_sellers_bvn, name='get_all_sellers_bvn'),
    path('get-all-seller-photo/', views.get_all_seller_photo, name='get_all_seller_photo'),
    path('get-all-sellers-bank-account/', views.get_all_sellers_bank_account, name='get_all_sellers_bank_account'),

    path('get-all-sellers/', views.get_all_sellers, name='get_all_sellers'),
    path('get-seller-account-detail/<str:seller_username>/', views.get_seller_account_detail, name='get_seller_account_detail'),
    path('verify-seller/', views.verify_seller, name='verify_seller'),

    path('get-paysofter-account-id/', views.get_paysofter_account_id, name='get_paysofter_account_id'),
    path('verify-paysofter-seller-id/', views.verify_paysofter_seller_id, name='verify_paysofter_seller_id'),
]
