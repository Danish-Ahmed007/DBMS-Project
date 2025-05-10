"""
Test script to verify email configuration
"""
import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

def test_email_sending():
    """Send a test email to verify configuration"""
    subject = 'Test Email from Django E-commerce App'
    message = 'This is a test email to verify that your email configuration is working correctly.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [settings.EMAIL_HOST_USER]  # Send to yourself
    
    print(f"Attempting to send email from {from_email} to {recipient_list[0]}...")
    
    try:
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False,
        )
        if result:
            print("✅ Success! Email was sent successfully.")
            print("If you don't see the email in your inbox, check your spam folder.")
        else:
            print("❌ Email was not sent. Check your email configuration.")
    except Exception as e:
        print(f"❌ An error occurred while sending the email: {str(e)}")
        print("Please check your email configuration settings.")

if __name__ == "__main__":
    test_email_sending()
