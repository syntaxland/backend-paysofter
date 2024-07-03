# payments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-payment/<int:payment_id>/', views.create_payment, name='create-payment'),
    path('get-payment-details/', views.PaymentDetailsView.as_view(), name='get_payment_details'),
]
