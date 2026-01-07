from django.urls import path
from . import views

app_name = 'userprofile'

urlpatterns = [
    path('register/', views.create_user, name='create_user'),
    path('register/checkout/', views.stripe_checkout, name='stripe_checkout'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
