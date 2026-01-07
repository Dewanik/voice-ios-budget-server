from django.urls import path
from . import views

app_name = 'expenses'

urlpatterns = [
    # Landing page at root
    path('', views.landing_page, name='landing_page'),
    
    # Expense reports (login required)
    path('today/', views.expenses_today, name='expenses_today'),
    path('week/', views.expenses_week, name='expenses_week'),
    path('month/', views.expenses_month, name='expenses_month'),
    path('month/<str:year_month>/', views.expenses_month_specific, name='expenses_month_specific'),
    path('range/', views.expenses_range, name='expenses_range'),
    path('budgets/', views.expenses_budgets, name='expenses_budgets'),
]