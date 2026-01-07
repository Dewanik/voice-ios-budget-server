# Stripe Configuration Guide

## Overview
Voice Budget now integrates with Stripe for user registration and monthly subscription payments ($5/month).

## Setup Instructions

### 1. Create Stripe Account
- Go to [stripe.com](https://stripe.com) and create an account
- Complete your account verification

### 2. Get Stripe API Keys
1. Login to your Stripe Dashboard
2. Navigate to **Developers** → **API Keys**
3. Copy your keys:
   - **Publishable Key** (starts with `pk_`)
   - **Secret Key** (starts with `sk_`)

### 3. Configure Azure Environment Variables
Add these environment variables to your Azure Web App:

```
STRIPE_PUBLIC_KEY=pk_your_key_here
STRIPE_SECRET_KEY=sk_your_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
BASE_URL=https://talk2ledger.azurewebsites.net
DEFAULT_FROM_EMAIL=noreply@talk2ledger.com
```

### 4. Setup Stripe Webhooks (for production)
1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Set endpoint URL to: `https://talk2ledger.azurewebsites.net/profile/webhook/stripe/`
4. Select events:
   - `customer.subscription.deleted`
   - `customer.subscription.updated`
   - `invoice.payment_failed`
5. Copy the **Signing Secret** and add to Azure as `STRIPE_WEBHOOK_SECRET`

### 5. Local Development Testing
For local testing, install Stripe CLI:
```bash
# macOS
brew install stripe/stripe-cli/stripe

# Linux
curl -s https://packages.stripe.dev/keys.asc | apt-key add -
echo "deb https://packages.stripe.dev/apt focal main" | tee /etc/apt/sources.list.d/stripe.list
apt update
apt install stripe

# Then run
stripe listen --forward-to localhost:8000/profile/webhook/stripe/
```

### 6. Email Configuration
For production email delivery:
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.your-email-provider.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
```

## User Registration Flow
1. User visits `/profile/register/`
2. Fills out registration form
3. Clicks "Proceed to Payment"
4. Redirected to Stripe Checkout
5. After successful payment:
   - User account created automatically
   - Login credentials sent via email
   - User logged in and redirected to profile

## Payment Success Handling
- Upon successful subscription payment, a `UserSubscription` record is created
- Email with login credentials is sent to user
- User is automatically logged in
- Subscription status is tracked and renewed automatically

## Subscription Management
Users can manage subscriptions through:
- Stripe Customer Portal: Add link in user profile (optional)
- Cancel/Update billing information through Stripe dashboard

## Testing Payment
Use Stripe test cards:
- **Success**: `4242 4242 4242 4242`
- **Decline**: `4000 0000 0000 0002`
- Any future expiry date and any 3-digit CVC

All test transactions use the `sk_test_` secret key.
