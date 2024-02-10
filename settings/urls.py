# settings/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('select-currency/', views.select_currency, name='select_currency'),
    # path('get-selected-currency/', views.get_selected_currency, name='get-selected-currency'),
]
  