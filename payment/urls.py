# transaction/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-payment/<int:payment_id>/', views.create_payment, name='create-payment'),
]
