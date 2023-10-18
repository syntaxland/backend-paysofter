from django.urls import path
from . import views

urlpatterns = [
    path('credit-point-balance/', views.get_credit_points_balance_view, name='credit-point-balance'),
    path('credit-point-request/', views.credit_point_request_view, name='credit_point_request'),
    
    path('get-all-credit-point-requests/', views.get_all_credit_points_request_view, name='get-all-credit-points'),
    path('get-credit-point/', views.get_user_credit_point_request_view, name='get-credit-point'),
    path('get-user-credit-point-earnings/', views.get_user_credit_point_earnings, name='get-user-credit-point-earnings'),

    path('get-user-credit-point-payments/', views.get_user_credit_point_payments, name='get-user-credit-point-payments'),
    path('get-all-credit-point-payments/', views.get_all_credit_point_payments, name='get-all-credit-point-payments'),
]
 