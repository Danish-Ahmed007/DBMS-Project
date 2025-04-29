from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Cart, CartItem

@login_required
def cart_view(request):
    """View current cart contents."""
    # Get or create cart for the logged-in user
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    """Add a product to the cart."""
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Check if product is already in cart
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    
    if not item_created:
        # If product already exists in cart, increment quantity
        cart_item.quantity += 1
        cart_item.save()
        messages.success(request, f"Added another {product.name} to your cart.")
    else:
        messages.success(request, f"{product.name} added to your cart.")
    
    return redirect('cart')

@login_required
def remove_from_cart(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    product_name = cart_item.product.name
    cart_item.delete()
    
    messages.success(request, f"{product_name} removed from your cart.")
    return redirect('cart')

@login_required
def update_quantity(request, item_id):
    """Update the quantity of an item in the cart."""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity > 0 and quantity <= cart_item.product.stock:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            messages.error(request, f"Invalid quantity. Available stock: {cart_item.product.stock}")
    
    return redirect('cart')
