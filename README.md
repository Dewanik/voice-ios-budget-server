# Voice iOS Budget Server

A Django-based server application that allows you to track personal expenses using voice commands through Siri on iOS devices. View detailed expense reports and manage budgets through a web interface with built-in security to ensure only authorized users can access sensitive financial data.

## Features

- **Voice-Activated Expense Tracking**: Add expenses via Siri shortcuts on iOS
- **Comprehensive Reporting**: View expenses by day, week, month, or custom date ranges
- **Budget Management**: Set and track budgets for overall spending and specific categories
- **Secure Access**: Authentication required for all expense reports and budget management
- **API Integration**: RESTful API for expense addition with token-based authentication
- **Data Visualization**: Charts and summaries for expense analysis

## Use Cases

### Personal Finance Management
- Track daily expenses like groceries, transportation, and entertainment
- Monitor spending patterns to identify areas for cost savings
- Set monthly budgets and receive visual feedback on budget adherence

### Voice-First Expense Logging
- Quickly log expenses while on the go using Siri voice commands
- No need to open apps or manually enter data - just speak to add expenses
- Perfect for cash transactions or impulse purchases

### Family Budget Tracking
- Shared expense tracking for households
- Monitor spending across different categories (groceries, utilities, entertainment)
- Generate reports for financial planning and discussions

### Business Expense Tracking
- Track business expenses with category-based organization
- Generate expense reports for reimbursement or tax purposes
- Maintain detailed notes for each expense entry

## iOS Setup

### Prerequisites
- iOS device with Siri enabled
- Internet connection for API calls
- The server must be running and accessible (locally or hosted)

### Setting Up Siri Shortcuts

1. **Install Shortcuts App**: Ensure the Shortcuts app is installed on your iOS device

2. **Create User Account**: 
   - Visit your server and create a user account via `/accounts/login/`
   - Or ask the administrator to create an account for you

3. **Create a New Shortcut**:
   - Open the Shortcuts app
   - Tap the "+" icon to create a new shortcut
   - Add an "Add to Siri" action

4. **Configure the Shortcut**:
   - Add a "Run Shortcut" action
   - Set the shortcut to call your server's API endpoint
   - Configure parameters for amount, category, username, password, and optional note

5. **One-Time Authentication Setup**:
   - When creating the shortcut, you'll need to provide your username and password
   - These credentials will be stored securely in the shortcut for future use
   - **Security Note**: Your password is stored locally on your device in the shortcut

6. **Example Shortcut Configuration**:
   ```
   URL: https://your-server.com/api/siri/add-expense/
   Method: POST
   Headers:
     Authorization: Bearer YOUR_SIRI_TOKEN
     Content-Type: application/json
   Body:
     {
       "username": "your_username",
       "password": "your_password",
       "amount": "Input from Siri",
       "category": "Input from Siri",
       "note": "Optional note",
       "request_id": "Unique ID for idempotency"
     }
   ```

7. **Configure User Credentials in Shortcut**:
   - In the Shortcuts app, when setting up the shortcut, you'll need to add your username and password
   - **Option A: Static Credentials (Recommended for personal use)**:
     - Add a "Text" action for username: Enter your username as plain text
     - Add a "Text" action for password: Enter your password as plain text
     - Connect these to the JSON body in the "Run Shortcut" action
   - **Option B: Ask for Credentials Each Time (More secure)**:
     - Add "Ask for Input" actions for both username and password
     - This will prompt you to enter credentials each time you use the shortcut
   - **Security Note**: For convenience, most users store credentials statically. Your password is only stored locally on your iOS device.

8. **Complete Shortcut Flow Example**:
   ```
   Shortcut Actions:
   1. Ask for Input: "Enter expense amount" → Store as "Amount"
   2. Ask for Input: "Enter category" → Store as "Category" 
   3. Text: "your_username" → Store as "Username"
   4. Text: "your_password" → Store as "Password"
   5. Run Shortcut:
      - URL: https://your-server.com/api/siri/add-expense/
      - Method: POST
      - Headers: Authorization: Bearer YOUR_SIRI_TOKEN
      - Body: {"username": Username, "password": Password, "amount": Amount, "category": Category}
   ```

9. **Voice Activation**:
   - Say "Hey Siri, add expense" followed by the amount and category
   - Example: "Hey Siri, add expense $25 for groceries"

### Environment Variables
Set the following environment variable on your server:
```
SIRI_TOKEN=your_secure_token_here
```

## Server Setup

### Prerequisites
- Python 3.8+
- Django 6.0+
- SQLite (default) or PostgreSQL/MySQL

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Dewanik/voice-ios-budget-server.git
   cd voice-ios-budget-server/apiAccess
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install django
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user. This user can access all reports and the Django admin interface.

6. **Create additional users** (optional):
   - Access the admin at `/admin/` after logging in as superuser
   - Or use Django shell: `python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('username', 'email@example.com', 'password')"`

The project includes custom login and logout templates for a consistent user experience.

### Running the Server

#### Development
```bash
python manage.py runserver
```
The server will be available at `http://127.0.0.1:8000`

#### Production
For production deployment, consider using:
- Gunicorn + Nginx
- Docker
- Heroku
- AWS/DigitalOcean droplets

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn apiAccess.wsgi --bind 0.0.0.0:8000
```

### Environment Configuration
Create a `.env` file in the project root with:
```
SIRI_TOKEN=your_secure_api_token
DEBUG=False
SECRET_KEY=your_django_secret_key
ALLOWED_HOSTS=your-domain.com
```

## Viewing Reports

All report views require user authentication. Access them at:

### Authentication
- **Login**: `/accounts/login/`
- **Logout**: `/accounts/logout/`
- **Admin Interface**: `/admin/` (superuser only)

### Available Reports

1. **Landing Page**: `/`
   - Public homepage showcasing features and getting started guide

2. **Today's Expenses**: `/today/`
   - Shows all expenses logged today

3. **This Week's Expenses**: `/week/`
   - Expenses from Monday to Sunday of the current week

4. **Current Month Expenses**: `/month/`
   - All expenses for the current month

5. **Specific Month**: `/month/YYYY-MM/`
   - View expenses for any specific month
   - Example: `/month/2024-01/`

6. **Custom Date Range**: `/range/?start=YYYY-MM-DD&end=YYYY-MM-DD`
   - View expenses between any two dates
   - Example: `/range/?start=2024-01-01&end=2024-01-31`

7. **Budget Management**: `/budgets/`
   - Set monthly budgets for overall spending or specific categories
   - View budget vs. actual spending comparisons

### Report Features
- **Expense Summaries**: Total spending and category breakdowns
- **Budget Tracking**: Visual indicators for budget adherence
- **Data Visualization**: Pie charts for expense distribution
- **Detailed Lists**: Individual expense entries with timestamps
- **Export Ready**: Data structured for easy export/analysis

## Security Protocol

### Authentication Requirements
- All expense report and budget management pages require user login
- API endpoints require both Bearer token authentication AND user credentials
- Admin interface accessible only to superusers
- Each user can only access their own expenses and budgets

### User Management
1. **Create Users**: Use Django admin or management commands
2. **Password Policies**: Enforced by Django's built-in validators
3. **Session Management**: Automatic logout on browser close
4. **Data Isolation**: Users cannot see other users' financial data

### API Security
- **Dual Authentication**: API calls require both `Authorization: Bearer <token>` header AND user credentials in request body
- **User Association**: All expenses are automatically linked to the authenticated user
- **Idempotency**: Prevents duplicate expense entries via request IDs
- **Input Validation**: Strict validation of amounts, categories, and data formats

### Siri Integration Security
- **Shortcut Authentication**: Users must configure their username/password in Siri shortcuts
- **Local Storage**: Credentials are stored securely on the user's iOS device
- **Token + User Verification**: Both server token and user credentials must be valid
- **One-Time Setup**: Authentication is configured once when creating the shortcut

### Data Protection
- **HTTPS Required**: Always use HTTPS in production
- **CSRF Protection**: Enabled for all forms
- **SQL Injection Prevention**: Django ORM protects against SQL injection
- **XSS Protection**: Template escaping prevents cross-site scripting

### Best Practices
- Use strong, unique passwords
- Regularly update the SIRI_TOKEN
- Keep Django and dependencies updated
- Monitor access logs for suspicious activity
- Use environment variables for sensitive configuration

## API Reference

### Authentication
All API endpoints require:
- **Bearer Token**: `Authorization: Bearer <SIRI_TOKEN>`
- **User Credentials**: For expense operations, include `username` and `password` in the request body

### Endpoints

#### `GET /api/siri/ping/`
Test API connectivity.
**Headers**: `Authorization: Bearer <token>`

#### `POST /api/siri/add-expense/`
Add a new expense for an authenticated user.
**Headers**: 
- `Authorization: Bearer <token>`
- `Content-Type: application/json`

**Body**:
```json
{
  "username": "your_username",
  "password": "your_password",
  "amount": 25.50,
  "category": "Groceries",
  "note": "Weekly shopping",
  "request_id": "optional-unique-id"
}
```

**Security Notes**:
- Expenses are automatically associated with the authenticated user
- Each user can only view their own expenses and budgets
- Failed authentication attempts are logged and rejected

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.