import stripe
import secrets
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .forms import RegisterUserForm
from .models import UserSubscription, UserProfile
from siriapi.models import Expense

# Set Stripe API key
stripe.api_key = settings.STRIPE_SECRET_KEY


def generate_random_password(length=12):
    """Generate a random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


def send_credentials_email(user, password):
    """Send login credentials to user email"""
    subject = 'Your Voice Budget Account Created'
    message = f"""
Welcome to Voice Budget!

Your account has been successfully created and activated.

Username: {user.username}
Email: {user.email}
Temporary Password: {password}

Please log in at: {settings.BASE_URL}/accounts/login/

You can change your password in your account settings after logging in.

Thank you for subscribing to Voice Budget!
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


@require_http_methods(["GET", "POST"])
def create_user(request):
    """Create user account with Stripe payment"""
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            # Store form data in session for after payment
            request.session['user_registration'] = {
                'username': form.cleaned_data['username'],
                'email': form.cleaned_data['email'],
                'password': form.cleaned_data['password'],
                'first_name': form.cleaned_data.get('first_name', ''),
                'last_name': form.cleaned_data.get('last_name', ''),
            }
            
            # Redirect to Stripe checkout
            return redirect('userprofile:stripe_checkout')
    else:
        form = RegisterUserForm()
    
    context = {
        'form': form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, 'userprofile/create_user.html', context)


@require_http_methods(["GET"])
def stripe_checkout(request):
    """Create Stripe checkout session"""
    if 'user_registration' not in request.session:
        return redirect('userprofile:create_user')
    
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Voice Budget - Monthly Subscription',
                            'description': '$5/month access to expense tracking',
                        },
                        'unit_amount': 500,  # $5.00 in cents
                        'recurring': {
                            'interval': 'month',
                            'interval_count': 1,
                        }
                    },
                    'quantity': 1,
                }
            ],
            mode='subscription',
            success_url=request.build_absolute_uri(reverse('userprofile:payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('userprofile:payment_cancel')),
            metadata={
                'user_registration': str(request.session['user_registration']),
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        return render(request, 'userprofile/payment_error.html', {'error': str(e)})


@require_http_methods(["GET"])
def payment_success(request):
    """Handle successful payment and create user account"""
    session_id = request.GET.get('session_id')
    
    if not session_id:
        return redirect('expenses:landing_page')
    
    if 'user_registration' not in request.session:
        return render(request, 'userprofile/payment_error.html', 
                     {'error': 'Session expired. Please try again.'})
    
    try:
        # Verify the session with Stripe
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.payment_status != 'paid':
            return render(request, 'userprofile/payment_error.html',
                         {'error': 'Payment not completed.'})
        
        # Create user account
        user_data = request.session['user_registration']
        user = User.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password'],
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', ''),
        )
        
        # Create user profile
        UserProfile.objects.create(user=user)
        
        # Create subscription record
        subscription = UserSubscription.objects.create(
            user=user,
            stripe_customer_id=session.customer,
            stripe_subscription_id=session.subscription,
            status='active',
            next_billing_date=timezone.now() + timedelta(days=30),
        )
        
        # Send credentials email
        send_credentials_email(user, user_data['password'])
        
        # Clear session
        del request.session['user_registration']
        
        # Log in the user
        user = authenticate(username=user_data['username'], password=user_data['password'])
        login(request, user)
        
        return render(request, 'userprofile/payment_success.html', {
            'username': user.username,
            'email': user.email,
        })
    
    except Exception as e:
        return render(request, 'userprofile/payment_error.html', {'error': str(e)})


@require_http_methods(["GET"])
def payment_cancel(request):
    """Handle cancelled payment"""
    if 'user_registration' in request.session:
        del request.session['user_registration']
    
    return render(request, 'userprofile/payment_cancel.html')


@login_required(login_url='/accounts/login/')
@require_http_methods(["GET"])
def user_profile(request):
    """Display user profile and subscription status"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    try:
        subscription = request.user.subscription
    except UserSubscription.DoesNotExist:
        subscription = None
    
    # Get user's recent expenses
    recent_expenses = Expense.objects.filter(user=request.user).order_by('-created_at')[:5]
    total_expenses = Expense.objects.filter(user=request.user).count()
    
    context = {
        'user_profile': user_profile,
        'subscription': subscription,
        'recent_expenses': recent_expenses,
        'total_expenses': total_expenses,
    }
    return render(request, 'userprofile/profile.html', context)


@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile information"""
    try:
        user_profile = request.user.profile
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    phone_number = request.POST.get('phone_number', '')
    user_profile.phone_number = phone_number
    user_profile.save()
    
    request.user.first_name = request.POST.get('first_name', '')
    request.user.last_name = request.POST.get('last_name', '')
    request.user.email = request.POST.get('email', '')
    request.user.save()
    
    return redirect('userprofile:user_profile')


@csrf_exempt
@require_http_methods(["POST"])
def stripe_webhook(request):
    """Handle Stripe webhooks"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    # Handle subscription events
    if event['type'] == 'customer.subscription.deleted':
        subscription_data = event['data']['object']
        try:
            subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription.status = 'cancelled'
            subscription.save()
        except UserSubscription.DoesNotExist:
            pass
    
    elif event['type'] == 'customer.subscription.updated':
        subscription_data = event['data']['object']
        try:
            subscription = UserSubscription.objects.get(
                stripe_subscription_id=subscription_data['id']
            )
            subscription.status = 'active'
            subscription.save()
        except UserSubscription.DoesNotExist:
            pass
    
    elif event['type'] == 'invoice.payment_failed':
        invoice_data = event['data']['object']
        try:
            customer_id = invoice_data['customer']
            subscription = UserSubscription.objects.get(
                stripe_customer_id=customer_id
            )
            subscription.status = 'failed'
            subscription.save()
        except UserSubscription.DoesNotExist:
            pass
    
    return HttpResponse(status=200)
