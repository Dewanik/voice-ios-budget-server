from datetime import datetime, timedelta
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from siriapi.models import Expense, Budget


def landing_page(request):
    """Public landing page showcasing the app features"""
    return render(request, 'expenses/landing.html')


def get_expenses_report(user, start_date, end_date, title):
    expenses = Expense.objects.filter(user=user, created_at__date__range=(start_date, end_date)).order_by('-created_at')
    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    totals_by_category = list(Expense.objects.filter(user=user, created_at__date__range=(start_date, end_date)).values('category').annotate(total=Sum('amount')).order_by('-total'))
    expenses_list = [
        {
            'id': e.id,
            'amount': e.amount,
            'category': e.category,
            'note': e.note,
            'created_at': e.created_at
        }
        for e in expenses
    ]

    # Budgets for the period (assuming monthly budgets)
    period_str = start_date.strftime('%Y-%m')
    budgets = Budget.objects.filter(user=user, period=period_str)
    overall_budget = budgets.filter(category='').first()
    category_budgets = {b.category: b.amount for b in budgets.exclude(category='')}

    # Add budget to each category
    for cat in totals_by_category:
        cat['budget'] = category_budgets.get(cat['category'])

    budget_info = {
        'overall_budget': overall_budget.amount if overall_budget else None,
        'category_budgets': category_budgets,
        'spent': total,
        'remaining': (overall_budget.amount - total) if overall_budget else None,
    }

    context = {
        'title': title,
        'period_start': start_date,
        'period_end': end_date,
        'total_amount': total,
        'totals_by_category': totals_by_category,
        'expenses': expenses_list,
        'budget_info': budget_info,
        'chart_data': totals_by_category,  # for pie chart
    }
    return context


@require_http_methods(["GET", "POST"])
@login_required
def expenses_week(request):
    if request.method == 'POST':
        # Redirect to range with selected dates
        start_str = request.POST.get('start')
        end_str = request.POST.get('end')
        if start_str and end_str:
            return redirect(f'/expenses/range/?start={start_str}&end={end_str}')
    now = timezone.now()
    monday = now - timedelta(days=now.weekday())
    start = monday.date()
    end = (monday + timedelta(days=6)).date()
    context = get_expenses_report(request.user, start, end, "This Week's Expenses")
    return render(request, 'expenses/report.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def expenses_month(request):
    if request.method == 'POST':
        month_str = request.POST.get('month')
        if month_str:
            return redirect(f'/expenses/month/{month_str}/')
    now = timezone.now()
    start = now.replace(day=1).date()
    end = now.date()
    context = get_expenses_report(request.user, start, end, "Current Month Expenses")
    return render(request, 'expenses/report.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def expenses_month_specific(request, year_month=None):
    if request.method == 'POST' or not year_month:
        if request.method == 'POST':
            year_month = request.POST.get('month')
        if not year_month:
            year_month = timezone.now().strftime('%Y-%m')
        return redirect(f'/expenses/month/{year_month}/')
    try:
        year, month = map(int, year_month.split('-'))
        start = datetime(year, month, 1).date()
        if month == 12:
            end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1).date() - timedelta(days=1)
        title = f"Expenses for {start.strftime('%B %Y')}"
    except ValueError:
        return render(request, 'expenses/error.html', {'error': 'Invalid month format. Use YYYY-MM'})
    context = get_expenses_report(request.user, start, end, title)
    return render(request, 'expenses/report.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def expenses_range(request):
    if request.method == 'POST':
        start_str = request.POST.get('start')
        end_str = request.POST.get('end')
        if start_str and end_str:
            return redirect(f'/expenses/range/?start={start_str}&end={end_str}')
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    if not start_str or not end_str:
        # Show form
        context = {'title': 'Select Date Range', 'show_form': True}
        return render(request, 'expenses/report.html', context)
    try:
        start = datetime.fromisoformat(start_str).date()
        end = datetime.fromisoformat(end_str).date()
        if start > end:
            return render(request, 'expenses/error.html', {'error': 'start must be before or equal to end'})
        title = f"Expenses from {start.strftime('%B %d, %Y')} to {end.strftime('%B %d, %Y')}"
    except ValueError:
        return render(request, 'expenses/error.html', {'error': 'Invalid date format. Use YYYY-MM-DD'})
    context = get_expenses_report(request.user, start, end, title)
    return render(request, 'expenses/report.html', context)


@require_http_methods(["GET"])
@login_required
def expenses_today(request):
    today = timezone.now().date()
    context = get_expenses_report(request.user, today, today, "Today's Expenses")
    return render(request, 'expenses/report.html', context)


@require_http_methods(["GET", "POST"])
@login_required
def expenses_budgets(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            period = request.POST.get('period')
            category = request.POST.get('category', '').strip()
            amount = request.POST.get('amount')
            if period and amount:
                try:
                    amount = float(amount)
                    Budget.objects.get_or_create(user=request.user, period=period, category=category, defaults={'amount': amount})
                except ValueError:
                    pass
        elif action == 'delete':
            budget_id = request.POST.get('budget_id')
            if budget_id:
                Budget.objects.filter(user=request.user, id=budget_id).delete()
        return redirect('/budgets/')

    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'title': 'Manage Budgets',
        'budgets': budgets,
        'show_budgets': True,
    }
    return render(request, 'expenses/budgets.html', context)
