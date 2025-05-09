# E-Commerce Store with Fraud Detection

A comprehensive Django-based e-commerce platform with integrated fraud detection capabilities, secure user authentication, product management, and order processing.

## Project Overview

This e-commerce platform demonstrates how to implement a secure online shopping experience with real-time fraud detection to protect both users and the business. It features a responsive design using Bootstrap, a complete shopping workflow, and an AI-ready fraud detection system.

## Key Features

### User Management
- Secure registration and authentication
- User profiles 
- Password management and validation

### Product Catalog
- Categorized product listings
- Detailed product views
- Image management

### Shopping Experience
- Responsive shopping cart
- Quantity management
- Checkout process

### Order Management
- Order creation and tracking
- Order status updates
- Order history for users
- Admin order management interface

### Fraud Detection System
- Real-time transaction analysis
- Risk scoring based on multiple factors
- Suspicious transaction flagging
- Email verification for flagged transactions
- Data collection for future ML integration

### Analytics
- User behavior tracking
- Purchase pattern analysis
- Conversion rate monitoring
- Performance metrics

## Technical Stack

- **Backend**: Django 5.x
- **Database**: PostgreSQL
- **Frontend**: Bootstrap, HTML, CSS
- **Authentication**: Django's authentication system with custom user model
- **Media Handling**: Django's file storage system

## Project Structure

The project is organized into several Django apps, each responsible for specific functionality:

- **users**: Custom user model and authentication
- **products**: Product catalog management
- **cart**: Shopping cart functionality
- **orders**: Order processing and management
- **fraud_detection**: Transaction analysis and verification
- **analytics**: Usage data tracking and analysis

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecommerce-fraud-detection.git
cd ecommerce-fraud-detection
```

2. Set up a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix/macOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables (create a .env file with):
```
SECRET_KEY=your_secret_key_here
DEBUG=True
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Start the development server:
```bash
python manage.py runserver
```

8. Access the application at http://127.0.0.1:8000/

## Fraud Detection System

The fraud detection system uses a rules-based approach that evaluates transactions based on various risk factors:

- Order amount compared to user's average orders
- Location mismatches between registration and checkout
- New accounts making large purchases
- Unusual order frequency
- Shipping/billing address mismatches
- Unusual purchase times
- Bulk orders of high-value items

Each factor contributes to a risk score, and transactions exceeding a threshold are flagged for verification.

### How It Works

1. During checkout, the system collects transaction data
2. Risk factors are evaluated and a risk score is calculated
3. If the score exceeds the threshold, the transaction is flagged
4. A verification email is sent to the user
5. The order is held until verified or the verification expires
6. All transaction data is stored for future analysis and ML training

## Admin Guide

### Fraud Dashboard

Access the fraud dashboard at `/admin/fraud_detection/` to:
- View flagged transaction statistics
- Monitor pending verifications
- Export transaction data for analysis
- Review flags by reason type

### Order Management

Access order management at `/admin/orders/` to:
- View all orders
- Update order statuses
- Access order details

## Development

### Adding New Features

1. Create a new Django app if necessary:
```bash
python manage.py startapp app_name
```

2. Add the app to INSTALLED_APPS in settings.py
3. Create models, views, and templates
4. Add URL patterns
5. Run migrations if needed:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Testing

Run the Django test suite:
```bash
python manage.py test
```

## Contributors

- Danish Ahmed
- Abdul Hakeem


