from django.contrib import admin
from .models import UserSubscription, UserProfile


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'stripe_customer_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'stripe_customer_id')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'created_at')
    search_fields = ('user__username', 'phone_number')
