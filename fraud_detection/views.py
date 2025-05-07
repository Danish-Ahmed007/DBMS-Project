from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.http import HttpResponse
from django.db.models import Count
from django.views.decorators.http import require_GET, require_POST
from django.urls import reverse
import csv
import uuid

from .models import TransactionData, FraudDetectionLog, FraudConfirmation
from orders.models import Order, OrderItem
from cart.models import Cart, CartItem

def is_staff(user):
    """Helper function to check if user is staff."""
    return user.is_authenticated and user.is_staff

@login_required
def verification_required_view(request, confirmation_key):
    """Show verification required page for flagged transactions."""
    confirmation = get_object_or_404(FraudConfirmation, confirmation_key=confirmation_key)
    
    # Check if user owns this confirmation or is staff
    if confirmation.transaction.user != request.user and not request.user.is_staff:
        messages.error(request, "You don't have permission to view this page.")
        return redirect('home')
    
    context = {
        'confirmation': confirmation,
        'transaction': confirmation.transaction,
        'fraud_log': confirmation.transaction.fraud_log
    }
    return render(request, 'fraud_detection/verification_required.html', context)

@login_required
@require_POST
def confirm_transaction(request, confirmation_key):
    """Handle user confirmation of a flagged transaction."""
    confirmation = get_object_or_404(
        FraudConfirmation, 
        confirmation_key=confirmation_key, 
        transaction__user=request.user,
        is_confirmed=False
    )
    
    if confirmation.is_expired:
        messages.error(request, "This confirmation link has expired. Please try your purchase again.")
        return redirect('home')
    
    # Mark as confirmed
    confirmation.is_confirmed = True
    confirmation.save()
    
    # Update the order status if it exists in the cart snapshot
    try:
        order_id = confirmation.cart_snapshot.get('order_id')
        if order_id:
            order = Order.objects.get(id=order_id)
            order.status = 'Processing'  # Update from Verification to Processing
            order.save()
            
            # Now we can redirect to the order detail page
            messages.success(request, "Thank you for confirming your transaction! Your order has been processed.")
            return redirect('order_detail', order_id=order.id)
    except (KeyError, Order.DoesNotExist):
        # If order doesn't exist for some reason, we'll create it
        try:
            # Process the order
            order = Order.objects.create(
                user=request.user,
                total_price=float(confirmation.cart_snapshot['total']),
                status='Processing'  # Set to Processing since it's confirmed
            )
            
            # Create order items from cart snapshot
            for item_data in confirmation.cart_snapshot['items']:
                OrderItem.objects.create(
                    order=order,
                    product_name=item_data['product_name'],
                    product_price=float(item_data['price']),
                    quantity=item_data['quantity'],
                    product_id=item_data['product_id']
                )
            
            # Clear the cart
            cart = Cart.objects.get(user=request.user)
            cart.items.all().delete()
            
            messages.success(request, "Thank you for confirming your transaction! Your order has been placed.")
            return redirect('order_detail', order_id=order.id)
        except Exception as e:
            messages.error(request, f"Error processing your order: {str(e)}")
            return redirect('home')
    
    messages.success(request, "Thank you for confirming your transaction!")
    return redirect('order_history')

@user_passes_test(is_staff)
def fraud_dashboard(request):
    """Admin dashboard showing fraud detection statistics."""
    # Recent flagged transactions
    recent_flagged = FraudDetectionLog.objects.filter(is_flagged=True).order_by('-detection_time')[:10]
    
    # Pending confirmations
    pending_confirmations = FraudConfirmation.objects.filter(
        is_confirmed=False,
        expiry_time__gt=timezone.now()
    ).order_by('expiry_time')[:10]
    
    # Summary statistics
    total_transactions = TransactionData.objects.count()
    flagged_count = FraudDetectionLog.objects.filter(is_flagged=True).count()
    confirmed_count = FraudConfirmation.objects.filter(is_confirmed=True).count()
    expired_count = FraudConfirmation.objects.filter(
        is_confirmed=False, 
        expiry_time__lt=timezone.now()
    ).count()
    
    flagged_percent = (flagged_count / total_transactions * 100) if total_transactions > 0 else 0
    
    # Flag reason breakdown
    all_flagged = FraudDetectionLog.objects.filter(is_flagged=True)
    reason_counts = {}
    
    for log in all_flagged:
        if 'reasons' in log.flag_reasons:
            for reason in log.flag_reasons['reasons']:
                key = reason.split(':')[0] if ':' in reason else reason
                reason_counts[key] = reason_counts.get(key, 0) + 1
    
    context = {
        'recent_flagged': recent_flagged,
        'pending_confirmations': pending_confirmations,
        'total_transactions': total_transactions,
        'flagged_count': flagged_count,
        'flagged_percent': round(flagged_percent, 1),
        'confirmed_count': confirmed_count,
        'expired_count': expired_count,
        'reason_counts': reason_counts
    }
    
    return render(request, 'fraud_detection/dashboard.html', context)

@user_passes_test(is_staff)
def export_transaction_data(request):
    """Export transaction data as CSV for future model training."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transaction_data.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Transaction ID',
        'User ID',
        'Order Total',
        'Location Match',
        'Is First Purchase',
        'Account Age (days)',
        'Transaction Hour',
        'Address Match',
        'Risk Score',
        'Is Flagged',
        'Was Confirmed',
        'Timestamp'
    ])
    
    # Get all transactions with related data
    transactions = TransactionData.objects.select_related('fraud_log').all()
    
    for transaction in transactions:
        # Try to get related confirmation
        try:
            confirmation = transaction.confirmation
            was_confirmed = confirmation.is_confirmed
        except FraudConfirmation.DoesNotExist:
            was_confirmed = None
        
        # Calculate location and address match
        location_match = transaction.confirmed_location == transaction.registration_location
        address_match = transaction.shipping_address == transaction.billing_address
        
        # Calculate account age
        account_age = (transaction.transaction_time - transaction.user.date_joined).days
        
        # Transaction hour
        transaction_hour = transaction.transaction_time.hour
        
        writer.writerow([
            transaction.id,
            transaction.user_id,
            transaction.order_total,
            location_match,
            transaction.is_first_purchase,
            account_age,
            transaction_hour,
            address_match,
            transaction.fraud_log.risk_score if hasattr(transaction, 'fraud_log') else None,
            transaction.fraud_log.is_flagged if hasattr(transaction, 'fraud_log') else None,
            was_confirmed,
            transaction.transaction_time.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    return response
