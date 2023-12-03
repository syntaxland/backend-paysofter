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
]
