from django.urls import path
from . import views

app_name = 'siriapi'

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('add-expense/', views.add_expense, name='add_expense'),
]