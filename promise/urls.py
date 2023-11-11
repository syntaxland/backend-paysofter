# promise/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('create-promise/', views.create_promise, name='create-promise'),
    
]
