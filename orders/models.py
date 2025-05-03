from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    """Order model for storing order information."""
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Accepted', 'Accepted'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Verification', 'Requires Verification'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"
    
    class Meta:
        ordering = ['-order_date']

class OrderItem(models.Model):
    """OrderItem model for storing order items."""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=200)  # Snapshot of product name at time of order
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Snapshot of price at time of order
    quantity = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)  # Reference to actual product
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name} in Order #{self.order.id}"
    
    @property
    def subtotal(self):
        """Calculate the subtotal price for this item."""
        return self.product_price * self.quantity
