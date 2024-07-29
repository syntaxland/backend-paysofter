# promise/urls.py
from django.urls import path
from . import views
 
urlpatterns = [
    path('create-promise/', views.create_promise, name='create-promise'),
    path('cancel-promise/', views.cancel_promise, name='cancel-promise'),
    path('get-buyer-promise/', views.get_buyer_promises, name='get-user-promise'),
    path('get-seller-promise/', views.get_seller_promises, name='get-seller-promise'), 
    path('get-seller-promises-test/', views.get_seller_promises_test, name='get_seller_promises_test'), 
    path('get-all-promises/', views.get_all_promises, name='get-all-promises'), 
    
    path('buyer-confirm-promise/', views.buyer_confirm_promise, name='buyer-confirm-promise'),
    path('seller-confirm-promise/', views.seller_confirm_promise, name='seller-confirm-promise'),

    path('buyer-create-promise-message/', views.buyer_create_promise_message, name='buyer_create_promise_message'),
    path('seller-create-promise-message/', views.seller_create_promise_message, name='seller_create_promise_message'),

    # path('list-promise-messages/<str:promise_id>/', views.list_promise_messages, name='list-promise-messages'),

    path('list-buyer-promise-messages/<str:promise_id>/', views.list_buyer_promise_messages, name='list_buyer_promise_messages'),
    path('list-seller-promise-messages/<str:promise_id>/', views.list_seller_promise_messages, name='list_seller_promise_messages'),

    path('clear-seller-promise-message-counter/', views.clear_seller_promise_message_counter, name='clear_seller_promise_message_counter'),
    path('clear-buyer-promise-message-counter/', views.clear_buyer_promise_message_counter, name='clear_buyer_promise_message_counter'),

    path('settle-disputed-promise/', views.settle_disputed_promise, name='settle-disputed-promise'),
]
