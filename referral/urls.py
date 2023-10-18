from django.urls import path
from . import views

urlpatterns = [   
    path("generate-referral-link/", views.generate_referral_link, name="generate-referral-link"),
#     path("generate-referral-link-button/", views.generate_referral_link_button, name="generate-referral-link-button"),
#     path("get-user-referrals/", views.get_user_referrals, name="get-user-referrals"),
#     path("get-all-referrals/", views.get_all_referrals, name="get-all-referrals"),
]
