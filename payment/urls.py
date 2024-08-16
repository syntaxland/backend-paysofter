# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-payment-link/', views.create_payment_link, name='create_payment_link'),
    path('update-payment-link/<int:pk>/', views.update_payment_link, name='update_payment_link'),
    path('delete-payment-link/<int:pk>/', views.update_payment_link, name='update_payment_link'),
    path('get-payment-link-detail/', views.get_payment_link_detail, name='get_payment_link_detail'),
    path('get-seller-payment-links/', views.get_seller_payment_links, name='get_seller_payment_links'),
    path('create-payment/<int:payment_id>/', views.create_payment, name='create-payment'),
    path('get-payment-details/', views.PaymentDetailsView.as_view(), name='get_payment_details'),
]
