from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_welcome_newsletter(email):
    """
    Send a welcome email to a new newsletter subscriber
    
    Parameters:
    - email: The subscriber's email address
    
    Returns:
    - bool: True if email was sent successfully, False otherwise
    """
    subject = 'Welcome to E-Commerce Store Newsletter'
    
    # Get current date in format "May 2025"
    from datetime import datetime
    current_date = datetime.now().strftime('%B %Y')
    
    # Context for email template
    context = {
        'email': email,
        'site_url': 'http://localhost:8000',  # In production, this would be your actual site URL
        'unsubscribe_url': '#', # In a real implementation, add an unsubscribe URL
        'current_date': current_date
    }
    
    # Render email template
    html_message = render_to_string('newsletter/email/welcome_email.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        # Send email
        send_mail(
            subject=subject,
            message=plain_message, 
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False
        )
        return True
    except Exception as e:
        print(f"Error sending newsletter email: {e}")
        return False
