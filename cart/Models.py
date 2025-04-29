from django.db import models
from django.conf import settings
from products.models import Product

class Cart(models.Model):
    """Cart model linked to user."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Cart for {self.user.username}"
    
    @property
    def total_price(self):
        """Calculate the total price of all items in the cart."""
        return sum(item.subtotal for item in self.items.all())
    
    @property
    def total_items(self):
        """Calculate the total number of items in the cart."""
        return self.items.count()

class CartItem(models.Model):
    """CartItem model with product and quantity."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart}"
    
    @property
    def subtotal(self):
        """Calculate the total price for this item."""
        return self.product.price * self.quantity
