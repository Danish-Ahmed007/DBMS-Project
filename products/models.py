from django.db import models
from django.urls import reverse

class Category(models.Model):
    """Category model for product categorization."""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        
    def __str__(self):
        return self.name

class Product(models.Model):
    """Product model for e-commerce items."""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('product_detail', args=[self.pk])
