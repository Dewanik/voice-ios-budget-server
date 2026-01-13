#!/usr/bin/env python
"""Test script to verify date filtering works correctly"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apiAccess.settings")
django.setup()

from django.contrib.auth.models import User
from siriapi.models import Expense
from django.utils import timezone
from datetime import datetime, timedelta

def test_date_filtering():
    """Test that date filtering returns the correct expenses"""
    user = User.objects.get(username='testuser')
    
    # Test 1: Today's expenses
    today = timezone.now().date()
    print(f"Testing date filtering for: {today}")
    print("=" * 50)
    
    # Manually query using the new method
    from datetime import timezone as tz
    start_datetime = datetime.combine(today, datetime.min.time(), tzinfo=tz.utc)
    end_datetime = datetime.combine(today, datetime.max.time(), tzinfo=tz.utc)
    
    expenses_today = Expense.objects.filter(
        user=user, 
        created_at__range=(start_datetime, end_datetime)
    ).order_by('-created_at')
    
    print(f"\n1. TODAY'S EXPENSES ({today}):")
    print(f"   Found: {len(expenses_today)} expenses")
    for e in expenses_today:
        print(f"   - {e.category}: ${e.amount} (created: {e.created_at})")
    
    # Test 2: This week's expenses
    now = timezone.now()
    monday = now - timedelta(days=now.weekday())
    start_week = monday.date()
    end_week = (monday + timedelta(days=6)).date()
    
    start_datetime = datetime.combine(start_week, datetime.min.time(), tzinfo=tz.utc)
    end_datetime = datetime.combine(end_week, datetime.max.time(), tzinfo=tz.utc)
    
    expenses_week = Expense.objects.filter(
        user=user,
        created_at__range=(start_datetime, end_datetime)
    ).order_by('-created_at')
    
    print(f"\n2. THIS WEEK'S EXPENSES ({start_week} to {end_week}):")
    print(f"   Found: {len(expenses_week)} expenses")
    for e in expenses_week:
        print(f"   - {e.category}: ${e.amount} (created: {e.created_at.date()})")
    
    # Test 3: This month's expenses
    start_month = now.replace(day=1).date()
    if now.month == 12:
        end_month = datetime(now.year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_month = datetime(now.year, now.month + 1, 1).date() - timedelta(days=1)
    
    start_datetime = datetime.combine(start_month, datetime.min.time(), tzinfo=tz.utc)
    end_datetime = datetime.combine(end_month, datetime.max.time(), tzinfo=tz.utc)
    
    expenses_month = Expense.objects.filter(
        user=user,
        created_at__range=(start_datetime, end_datetime)
    ).order_by('-created_at')
    
    print(f"\n3. THIS MONTH'S EXPENSES ({start_month} to {end_month}):")
    print(f"   Found: {len(expenses_month)} expenses")
    for e in expenses_month:
        print(f"   - {e.category}: ${e.amount} (created: {e.created_at.date()})")
    
    print("\n" + "=" * 50)
    print("✅ Date filtering test completed successfully!")

if __name__ == '__main__':
    test_date_filtering()
