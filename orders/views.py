from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import transaction
from django.utils import timezone
import time

from cart.models import Cart
from .models import Order, OrderItem
from fraud_detection.services import FraudDetectionService

@login_required
def checkout_view(request):
    """Handle checkout process with fraud detection."""
    try:
        cart = Cart.objects.get(user=request.user)
        if cart.items.count() == 0:
            messages.error(request, "Your cart is empty.")
            return redirect('cart')
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect('cart')

    if request.method == 'POST':
        # Get user confirmed location and addresses from form
        confirmed_location = request.POST.get('confirmed_location', '')
        shipping_address = request.POST.get('shipping_address', '')
        billing_address = request.POST.get('billing_address', '')
        
        # Simulate processing delay for UX (3-5 seconds)
        time.sleep(3)
        
        # Initialize fraud detection service
        fraud_service = FraudDetectionService(
            user=request.user,
            cart=cart,
            confirmed_location=confirmed_location,
            shipping_address=shipping_address, 
            billing_address=billing_address
        )
        
        # Collect transaction data
        transaction_data = fraud_service.collect_transaction_data()
        
        # Run fraud detection rules
        is_flagged = fraud_service.run_fraud_detection()
        
        if is_flagged:
            # Create fraud confirmation entry
            confirmation = fraud_service.create_fraud_confirmation()
            
            # Redirect to verification page
            messages.warning(request, "Your transaction requires additional verification.")
            return redirect('verification_required', confirmation_key=confirmation.confirmation_key)
        else:
            # Create order from cart items if no flags
            with transaction.atomic():
                # Calculate total price
                total_price = cart.total_price
                
                # Create order
                order = Order.objects.create(
                    user=request.user,
                    total_price=total_price,
                    status='Pending'
                )
                
                # Create order items from cart items
                for cart_item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product_name=cart_item.product.name,
                        product_price=cart_item.product.price,
                        quantity=cart_item.quantity,
                        product=cart_item.product
                    )
                    
                    # Update product stock
                    product = cart_item.product
                    product.stock -= cart_item.quantity
                    product.save()
                
                # Clear the cart
                cart.items.all().delete()
                
                messages.success(request, f"Your order #{order.id} has been placed successfully!")
                return redirect('order_detail', order_id=order.id)
    
    return render(request, 'orders/checkout.html', {'cart': cart})

@login_required
def order_history_view(request):
    """Display order history for the current user."""
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_history.html', {'orders': orders})

@login_required
def order_detail_view(request, order_id):
    """Display details of a specific order."""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        return render(request, 'orders/order_detail.html', {'order': order})
    except Order.DoesNotExist:
        messages.error(request, "Order not found.")
        return redirect('order_history')

# Check if user is staff
def is_staff(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff)
def order_management_view(request):
    """Display all orders for staff to manage."""
    orders = Order.objects.all().order_by('-order_date')
    return render(request, 'orders/order_management.html', {'orders': orders})

@user_passes_test(is_staff)
def update_order_status(request, order_id):
    """Update the status of an order (staff only)."""
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
            messages.success(request, f"Order #{order.id} status updated to {new_status}")
        else:
            messages.error(request, "Invalid status selected")
            
    return redirect('order_management')
