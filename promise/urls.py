# promise/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-promise/', views.create_promise, name='create-promise'),
    path('get-buyer-promise/', views.get_buyer_promises, name='get-user-promise'),
    path('get-seller-promise/', views.get_seller_promises, name='get-seller-promise'),
    path('buyer-confirm-promise/', views.buyer_confirm_promise, name='buyer-confirm-promise'),
    path('seller-confirm-promise/', views.seller_confirm_promise, name='seller-confirm-promise'),
]
 