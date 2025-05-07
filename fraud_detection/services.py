from django.utils import timezone
from django.db.models import Avg, Count
import json
from datetime import timedelta
from .models import TransactionData, FraudDetectionLog, FraudConfirmation
from orders.models import Order, OrderItem
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

class FraudDetectionService:
    """Service class for fraud detection operations"""
    
    def __init__(self, user, cart, confirmed_location, shipping_address, billing_address):
        """Initialize with transaction data"""
        self.user = user
        self.cart = cart
        self.confirmed_location = confirmed_location
        self.shipping_address = shipping_address
        self.billing_address = billing_address
        self.order_total = cart.total_price
        self.transaction_data = None
        self.fraud_log = None
    
    def collect_transaction_data(self):
        """Collect and store all transaction data"""
        # Calculate user's previous order average
        user_orders = Order.objects.filter(user=self.user)
        order_average = user_orders.aggregate(avg=Avg('total_price'))['avg'] or 0.00
        
        # Check if this is user's first purchase
        is_first_purchase = user_orders.count() == 0
        
        # Get user's device info (in a real system, this would be collected from request headers)
        device_info = {
            'user_agent': 'Demo User Agent',
            'ip_address': '127.0.0.1',
        }
        
        # Create transaction data
        self.transaction_data = TransactionData.objects.create(
            user=self.user,
            order_total=self.order_total,
            confirmed_location=self.confirmed_location,
            registration_location=self.user.location,
            device_info=device_info,
            shipping_address=self.shipping_address,
            billing_address=self.billing_address,
            is_first_purchase=is_first_purchase,
            user_order_average=order_average
        )
        
        # Create fraud log
        self.fraud_log = FraudDetectionLog.objects.create(
            transaction=self.transaction_data,
            is_flagged=False,
            risk_score=0
        )
        
        return self.transaction_data
    
    def run_fraud_detection(self):
        """Run all fraud detection rules and return whether the transaction is flagged"""
        risk_score = 0
        
        # Rule 1: Flag if order amount is 200% higher than user's average order
        if not self.transaction_data.is_first_purchase and self.transaction_data.user_order_average > 0:
            if self.order_total > (self.transaction_data.user_order_average * 2):
                self.fraud_log.add_flag_reason(
                    f"Order amount (${self.order_total}) is significantly higher than user's average (${self.transaction_data.user_order_average})"
                )
                risk_score += 25
        
        # Rule 2: Flag if user confirms a different location during checkout than registration
        if self.transaction_data.confirmed_location != self.transaction_data.registration_location:
            self.fraud_log.add_flag_reason(
                f"Location mismatch: Checkout location '{self.transaction_data.confirmed_location}' differs from registration location '{self.transaction_data.registration_location}'"
            )
            risk_score += 20
        
        # Rule 3: Flag if account is less than 48 hours old and order exceeds $150
        account_age = timezone.now() - self.user.date_joined
        if account_age < timedelta(hours=48) and self.order_total > 150:
            self.fraud_log.add_flag_reason(
                f"New account (age: {account_age.days} days, {int(account_age.seconds/3600)} hours) with large order (${self.order_total})"
            )
            risk_score += 30
        
        # Rule 4: Flag if user has placed 4+ orders in last 24 hours
        recent_order_count = Order.objects.filter(
            user=self.user,
            order_date__gte=timezone.now() - timedelta(hours=24)
        ).count()
        
        if recent_order_count >= 3:  # 3 previous orders + current = 4
            self.fraud_log.add_flag_reason(
                f"High order frequency: {recent_order_count + 1} orders in the last 24 hours"
            )
            risk_score += 20
        
        # Rule 5: Flag if shipping/billing addresses differ and order exceeds $200
        if self.shipping_address != self.billing_address and self.order_total > 200:
            self.fraud_log.add_flag_reason(
                f"Address mismatch with order exceeding $200"
            )
            risk_score += 15
        
        # Rule 6: Flag if checkout occurs between 1am-5am local time and differs from user's usual patterns
        current_hour = timezone.localtime().hour
        if 1 <= current_hour <= 5:
            # Check user's previous order hours (simplified for demo)
            unusual_hour = True  # In a real system, you'd determine this from history
            
            if unusual_hour:
                self.fraud_log.add_flag_reason(
                    f"Unusual order time: {current_hour}:00 (unusual for this user)"
                )
                risk_score += 10
        
        # Rule 7: Flag if order contains 5+ of the same high-value item
        high_value_items = {}
        for item in self.cart.items.all():
            if item.product.price > 50:  # Define high value as > $50
                if item.product.id in high_value_items:
                    high_value_items[item.product.id]['quantity'] += item.quantity
                else:
                    high_value_items[item.product.id] = {
                        'name': item.product.name,
                        'quantity': item.quantity
                    }
        
        for product_id, data in high_value_items.items():
            if data['quantity'] >= 5:
                self.fraud_log.add_flag_reason(
                    f"Bulk order of high-value item: {data['quantity']} x {data['name']}"
                )
                risk_score += 25
                break
        
        # Update risk score and flagged status
        self.fraud_log.risk_score = risk_score
        self.fraud_log.is_flagged = risk_score >= 40  # Flag if risk score reaches threshold
        self.fraud_log.save()
        
        return self.fraud_log.is_flagged
    
    def create_fraud_confirmation(self):
        """Create a fraud confirmation entry for flagged transactions"""
        if not self.fraud_log.is_flagged:
            return None
            
        # Create cart snapshot
        cart_items = []
        for item in self.cart.items.all():
            cart_items.append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': str(item.product.price),
                'subtotal': str(item.subtotal)
            })
            
        cart_snapshot = {
            'items': cart_items,
            'total': str(self.cart.total_price)
        }
        
        # Set expiry time 30 minutes from now
        expiry_time = timezone.now() + timedelta(minutes=30)
        
        # Create order with Verification status
        with transaction.atomic():
            # Create order
            pending_order = Order.objects.create(
                user=self.user,
                total_price=self.order_total,
                status='Verification'  # Set status to Requires Verification
            )
            
            # Create order items
            for item in self.cart.items.all():
                OrderItem.objects.create(
                    order=pending_order,
                    product_name=item.product.name,
                    product_price=item.product.price,
                    quantity=item.quantity,
                    product=item.product
                )
        
        # Create confirmation
        confirmation = FraudConfirmation.objects.create(
            transaction=self.transaction_data,
            expiry_time=expiry_time,
            cart_snapshot=cart_snapshot
        )
        
        # Store order ID in the cart snapshot for reference
        confirmation.cart_snapshot['order_id'] = pending_order.id
        confirmation.save()
        
        return confirmation
