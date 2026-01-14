#!/usr/bin/env python
"""Test script to verify user data isolation and persistence"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apiAccess.settings")
django.setup()

from django.contrib.auth.models import User
from siriapi.models import Expense, Budget
from userprofile.models import UserProfile, UserSubscription
from django.utils import timezone
from django.test import Client
from django.urls import reverse

def test_user_data_isolation():
    """Test that data isolation works correctly between users"""
    
    # Clean up first
    User.objects.filter(username__in=['testuser1', 'testuser2']).delete()
    
    print("=" * 60)
    print("Testing User Data Isolation and Persistence")
    print("=" * 60)
    
    # Create two test users
    user1 = User.objects.create_user(
        username='testuser1',
        email='test1@example.com',
        password='testpass123'
    )
    user2 = User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass456'
    )
    
    # Create profiles
    UserProfile.objects.create(user=user1)
    UserProfile.objects.create(user=user2)
    
    print(f"\n1. Created two users:")
    print(f"   - {user1.username}")
    print(f"   - {user2.username}")
    
    # Create expenses for user1
    exp1_1 = Expense.objects.create(
        user=user1,
        amount=50.00,
        category='Food',
        note='Lunch'
    )
    exp1_2 = Expense.objects.create(
        user=user1,
        amount=25.00,
        category='Transport',
        note='Gas'
    )
    
    print(f"\n2. Created {Expense.objects.filter(user=user1).count()} expenses for {user1.username}")
    
    # Create expenses for user2
    exp2_1 = Expense.objects.create(
        user=user2,
        amount=100.00,
        category='Shopping',
        note='Clothes'
    )
    
    print(f"   Created {Expense.objects.filter(user=user2).count()} expenses for {user2.username}")
    
    # Verify isolation
    user1_expenses = Expense.objects.filter(user=user1)
    user2_expenses = Expense.objects.filter(user=user2)
    
    print(f"\n3. Verifying data isolation:")
    print(f"   User1 expenses: {user1_expenses.count()} (expected: 2)")
    print(f"   User2 expenses: {user2_expenses.count()} (expected: 1)")
    
    for exp in user1_expenses:
        print(f"      - {exp.category}: ${exp.amount}")
    
    print(f"\n   User2 expenses:")
    for exp in user2_expenses:
        print(f"      - {exp.category}: ${exp.amount}")
    
    # Test Login Redirect
    print(f"\n4. Testing login redirect behavior:")
    client = Client()
    
    # Login as user1
    login_success = client.login(username='testuser1', password='testpass123')
    print(f"   Logged in as {user1.username}: {login_success}")
    
    # Check where we get redirected after login
    response = client.get(reverse('userprofile:user_profile'))
    print(f"   Profile page status: {response.status_code}")
    
    # Verify the user in the response
    if response.status_code == 200:
        print(f"   ✓ User can access their profile")
    else:
        print(f"   ✗ ERROR: User cannot access their profile")
    
    # Check that user1 sees only their expenses
    from expenses.views import get_expenses_report
    from datetime import datetime, timedelta
    
    today = timezone.now().date()
    context = get_expenses_report(user1, today - timedelta(days=30), today, "Test")
    print(f"\n5. Expense visibility test:")
    print(f"   User1 can see: {len(context['expenses'])} expenses (expected: 2)")
    
    # Logout and login as user2
    client.logout()
    login_success2 = client.login(username='testuser2', password='testpass456')
    print(f"\n6. Logout and login as {user2.username}: {login_success2}")
    
    # Check user2 sees only their expenses
    context2 = get_expenses_report(user2, today - timedelta(days=30), today, "Test")
    print(f"   User2 can see: {len(context2['expenses'])} expenses (expected: 1)")
    
    # Verify data persistence
    print(f"\n7. Data Persistence Check:")
    print(f"   Total expenses in DB: {Expense.objects.count()}")
    print(f"   User1 still has: {Expense.objects.filter(user=user1).count()} expenses")
    print(f"   User2 still has: {Expense.objects.filter(user=user2).count()} expenses")
    
    # Verify data didn't vanish
    if Expense.objects.filter(user=user1).count() == 2:
        print(f"   ✓ User1 data persisted correctly")
    else:
        print(f"   ✗ ERROR: User1 data vanished!")
    
    if Expense.objects.filter(user=user2).count() == 1:
        print(f"   ✓ User2 data persisted correctly")
    else:
        print(f"   ✗ ERROR: User2 data vanished!")
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)
    
    # Cleanup
    User.objects.filter(username__in=['testuser1', 'testuser2']).delete()

if __name__ == '__main__':
    test_user_data_isolation()
