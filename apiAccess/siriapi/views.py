import json
import logging
import os
from decimal import Decimal, InvalidOperation
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate
from .models import Expense, SiriRequest

logger = logging.getLogger(__name__)

SIRI_TOKEN = os.environ.get('SIRI_TOKEN')

def authenticate_token(request):
    """Authenticate using Bearer token only"""
    if not SIRI_TOKEN:
        logger.error("SIRI_TOKEN environment variable is not set")
        return False
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header[7:]  # Remove 'Bearer '
    return token == SIRI_TOKEN


def authenticate_user(request):
    """Authenticate user with token + username/password"""
    # First check token
    if not authenticate_token(request):
        logger.warning("Token authentication failed")  # Moved before return for reachability
        return None
    
    # Then check user credentials
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
        else:  # GET request
            data = request.GET.dict()
        
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            logger.warning("Missing username or password")
            return None
            
        user = authenticate(username=username, password=password)
        if not user:
            logger.warning(f"User authentication failed for username: {username}")
        
        return user
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error parsing request data: {e}")
        return None

@csrf_exempt
@require_http_methods(["GET"])
def ping(request):
    if not authenticate_token(request):
        return JsonResponse({'ok': False, 'error': 'Unauthorized'}, status=401)
    return JsonResponse({'ok': True, 'message': 'pong'})

@csrf_exempt
@require_http_methods(["GET", "POST"])
def add_expense(request):
    user = authenticate_user(request)
    if not user:
        return JsonResponse({'ok': False, 'error': 'Unauthorized - invalid credentials'}, status=401)
    
    # Get data from POST body or GET parameters
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)
    else:  # GET request (for debugging)
        data = request.GET.dict()
        # Note: GET requests are not recommended for production use with sensitive data
    
    amount = data.get('amount')
    category = data.get('category', '').strip()
    note = data.get('note', '')
    request_id = data.get('request_id')

    # Validate amount
    try:
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError
    except (TypeError, ValueError, InvalidOperation):
        return JsonResponse({'ok': False, 'error': 'Invalid amount: must be a positive number'}, status=400)

    # Validate category
    if not category:
        return JsonResponse({'ok': False, 'error': 'Category is required'}, status=400)
    if len(category) > 80:
        return JsonResponse({'ok': False, 'error': 'Category too long (max 80 characters)'}, status=400)

    # Idempotency check
    if request_id:
        if SiriRequest.objects.filter(request_id=request_id, endpoint='add-expense').exists():
            return JsonResponse({
                'ok': True,
                'message': 'Already processed',
                'expense_id': None,
                'created_at': None
            })

    # Create expense
    expense = Expense.objects.create(user=user, amount=amount, category=category, note=note)

    # Record request_id if provided
    if request_id:
        SiriRequest.objects.create(request_id=request_id, endpoint='add-expense')

    logger.info(f"Added expense: {expense}")

    return JsonResponse({
        'ok': True,
        'message': f"Added expense ${expense.amount} to {expense.category}",
        'expense_id': expense.id,
        'created_at': expense.created_at.isoformat()
    })