from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from .models import NewsletterSubscription
from .email_service import send_welcome_newsletter

def test_newsletter_view(request):
    """
    A simple view to test the newsletter subscription functionality
    """
    return render(request, 'newsletter/test_subscription.html')

@require_POST
@csrf_exempt
def subscribe_newsletter(request):
    """Handle newsletter subscription requests"""
    try:
        # Try to get email from JSON data
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                email = data.get('email')
            except json.JSONDecodeError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid JSON format'
                }, status=400)
        else:
            # Get email from form data
            email = request.POST.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required'
            }, status=400)
            
        # Check if already subscribed
        existing = NewsletterSubscription.objects.filter(email=email).first()
        
        if existing:
            if existing.is_active:
                return JsonResponse({
                    'success': False,
                    'error': 'Email is already subscribed to the newsletter'
                })
            else:
                # Reactivate subscription
                existing.is_active = True
                existing.save()
                
                # Send welcome email
                send_welcome_newsletter(email)
                
                return JsonResponse({
                    'success': True,
                    'message': 'Your subscription has been reactivated'
                })
        
        # Create new subscription
        subscription = NewsletterSubscription.objects.create(email=email)
        
        # Send welcome email
        send_welcome_newsletter(email)
        
        # Return success response
        return JsonResponse({
            'success': True,
            'message': 'Thank you for subscribing to our newsletter!'
        })
          except Exception as e:
        import traceback
        print(f"Exception in newsletter subscription: {e}")
        print(traceback.format_exc())
        return JsonResponse({
            'success': False,
            'error': f"Server error: {str(e)}"
        }, status=500)
