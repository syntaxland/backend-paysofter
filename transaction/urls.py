# transaction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('initiate-transaction/', views.initiate_transaction, name='initiate-transaction'),
    path('get-user-transactions/', views.get_user_transactions, name='get-user-transactions'), 
]
 