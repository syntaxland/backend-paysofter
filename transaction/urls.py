# transaction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('get-api-key-status/', views.get_api_key_status, name='get_api_key_status'),
    path('initiate-transaction/', views.initiate_transaction, name='initiate-transaction'),
    path('get-user-transactions/', views.get_user_transactions, name='get-user-transactions'), 
    path('get-user-test-transactions/', views.get_user_test_transactions, name='get_user_test_transactions'), 
]
 