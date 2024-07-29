# settings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('select-currency/', views.select_currency, name='select_currency'),
    path('toggle-api-key-status/', views.toggle_api_key_status, name='toggle_api_key_status'),
]
  