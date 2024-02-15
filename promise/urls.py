# promise/urls.py
from django.urls import path
from . import views
 
urlpatterns = [
    path('create-promise/', views.create_promise, name='create-promise'),
    path('cancel-promise/', views.cancel_promise, name='cancel-promise'),
    path('get-buyer-promise/', views.get_buyer_promises, name='get-user-promise'),
    path('get-seller-promise/', views.get_seller_promises, name='get-seller-promise'), 
    path('get-all-promises/', views.get_all_promises, name='get-all-promises'), 
    
    path('buyer-confirm-promise/', views.buyer_confirm_promise, name='buyer-confirm-promise'),
    path('seller-confirm-promise/', views.seller_confirm_promise, name='seller-confirm-promise'),

    path('create-promise-messages/', views.create_promise_message, name='create-promise-messages'),
    path('settle-disputed-promise/', views.settle_disputed_promise, name='settle-disputed-promise'),
    path('list-promise-messages/<str:promise_id>/', views.list_promise_messages, name='list-promise-messages'),
]
