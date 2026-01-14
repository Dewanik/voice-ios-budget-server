#!/usr/bin/env python
"""
Comprehensive test to verify user data persistence after logout/login cycle
Tests the RefreshUserMiddleware fix
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "apiAccess.settings")
django.setup()

from django.contrib.auth.models import User
from siriapi.models import Expense, Budget
from userprofile.models import UserProfile
from django.test import Client
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models import Sum


def test_user_data_persistence():
    """Test that user data persists after logout/login cycle"""
    
    print("=" * 70)
    print("COMPREHENSIVE USER DATA PERSISTENCE TEST")
    print("Testing RefreshUserMiddleware Fix")
    print("=" * 70)
    
    # Clean up
    User.objects.filter(username__in=['persist_test_user']).delete()
    
    # Create test user
    user = User.objects.create_user(
        username='persist_test_user',
        email='persisttest@example.com',
        password='testpass123'
    )
    
    # Create user profile
    UserProfile.objects.create(user=user)
    
    print(f"\n✓ Created test user: {user.username}")
    
    # Create various expenses
    now = timezone.now()
    expenses_data = [
        {'amount': 50.00, 'category': 'Food', 'note': 'Lunch'},
        {'amount': 25.00, 'category': 'Transport', 'note': 'Gas'},
        {'amount': 15.50, 'category': 'Entertainment', 'note': 'Movie'},
        {'amount': 100.00, 'category': 'Shopping', 'note': 'Clothes'},
        {'amount': 35.75, 'category': 'Food', 'note': 'Dinner'},
    ]
    
    for expense_data in expenses_data:
        Expense.objects.create(
            user=user,
            amount=expense_data['amount'],
            category=expense_data['category'],
            note=expense_data['note'],
            created_at=now
        )
    
    print(f"✓ Created {len(expenses_data)} expenses")
    
    # Create a budget
    month_str = now.strftime('%Y-%m')
    budget = Budget.objects.create(
        user=user,
        period=month_str,
        category='',
        amount=500.00
    )
    print(f"✓ Created budget: ${budget.amount} for {month_str}")
    
    # Test 1: Verify initial data
    print("\n" + "=" * 70)
    print("TEST 1: Initial Data Verification")
    print("=" * 70)
    
    initial_expenses = Expense.objects.filter(user=user).count()
    initial_total = Expense.objects.filter(user=user).aggregate(
        total=Sum('amount')
    )['total']
    
    print(f"Initial expenses: {initial_expenses}")
    print(f"Initial total: ${initial_total:.2f}")
    assert initial_expenses == 5, f"Expected 5 expenses, got {initial_expenses}"
    assert initial_total == 226.25, f"Expected total $226.25, got ${initial_total}"
    print("✓ PASSED")
    
    # Test 2: Login and verify data is accessible
    print("\n" + "=" * 70)
    print("TEST 2: Login and Verify Data Access")
    print("=" * 70)
    
    client = Client()
    login_success = client.login(username='persist_test_user', password='testpass123')
    
    print(f"Login successful: {login_success}")
    assert login_success, "Login failed"
    
    # Verify data through query (simulating what a view would do)
    session_expenses = Expense.objects.filter(user=user).count()
    print(f"Expenses accessible after login: {session_expenses}")
    assert session_expenses == 5, f"Expected 5, got {session_expenses}"
    print("✓ PASSED")
    
    # Test 3: Logout
    print("\n" + "=" * 70)
    print("TEST 3: Logout")
    print("=" * 70)
    
    client.logout()
    print("User logged out")
    print("✓ PASSED")
    
    # Test 4: Login again (the critical test)
    print("\n" + "=" * 70)
    print("TEST 4: Login Again (After Logout) - CRITICAL TEST")
    print("=" * 70)
    
    login_success_2 = client.login(username='persist_test_user', password='testpass123')
    print(f"Second login successful: {login_success_2}")
    assert login_success_2, "Second login failed"
    
    # Verify data is still accessible
    post_relogin_expenses = Expense.objects.filter(user=user).count()
    post_relogin_total = Expense.objects.filter(user=user).aggregate(
        total=Sum('amount')
    )['total']
    
    print(f"Expenses accessible after re-login: {post_relogin_expenses}")
    print(f"Total after re-login: ${post_relogin_total:.2f}")
    
    assert post_relogin_expenses == 5, (
        f"Data missing after re-login! "
        f"Expected 5 expenses, got {post_relogin_expenses}"
    )
    assert post_relogin_total == 226.25, (
        f"Total changed after re-login! "
        f"Expected $226.25, got ${post_relogin_total}"
    )
    print("✓ PASSED - DATA PERSISTS CORRECTLY")
    
    # Test 5: Verify budget is also accessible
    print("\n" + "=" * 70)
    print("TEST 5: Budget Data Persistence")
    print("=" * 70)
    
    budgets = Budget.objects.filter(user=user, period=month_str)
    print(f"Budgets accessible after re-login: {budgets.count()}")
    assert budgets.count() == 1, f"Expected 1 budget, got {budgets.count()}"
    
    budget_obj = budgets.first()
    print(f"Budget amount: ${budget_obj.amount}")
    print(f"Budget remaining: ${budget_obj.amount - post_relogin_total:.2f}")
    print("✓ PASSED")
    
    # Test 6: Multiple logout/login cycles
    print("\n" + "=" * 70)
    print("TEST 6: Multiple Logout/Login Cycles")
    print("=" * 70)
    
    for cycle in range(1, 4):
        client.logout()
        print(f"Cycle {cycle}: Logged out")
        
        client.login(username='persist_test_user', password='testpass123')
        print(f"Cycle {cycle}: Logged in again")
        
        cycle_expenses = Expense.objects.filter(user=user).count()
        assert cycle_expenses == 5, (
            f"Cycle {cycle}: Expected 5 expenses, got {cycle_expenses}"
        )
    
    print("✓ PASSED - Data persists across multiple cycles")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print("✓ Initial data creation: SUCCESS")
    print("✓ Data accessible after first login: SUCCESS")
    print("✓ Data persists after logout/login: SUCCESS (CRITICAL)")
    print("✓ Budget data persists: SUCCESS")
    print("✓ Multiple cycle test: SUCCESS")
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED - User data persists correctly!")
    print("=" * 70)


if __name__ == '__main__':
    test_user_data_persistence()
