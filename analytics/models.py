from django.db import models
from django.conf import settings
from products.models import Product, Category
from django.utils import timezone
import datetime

class PageView(models.Model):
    """Track page views for analytics purposes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    page_url = models.CharField(max_length=255)
    view_time = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.page_url} viewed at {self.view_time}"
    
    class Meta:
        indexes = [
            models.Index(fields=['view_time']),
            models.Index(fields=['page_url']),
        ]

class ProductView(models.Model):
    """Track when products are viewed"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    view_time = models.DateTimeField(auto_now_add=True)
    session_id = models.CharField(max_length=100, null=True, blank=True)
    
    def __str__(self):
        return f"{self.product.name} viewed at {self.view_time}"
    
    class Meta:
        indexes = [
            models.Index(fields=['view_time']),
            models.Index(fields=['product']),
        ]

class SearchQuery(models.Model):
    """Track user search queries"""
    query_text = models.CharField(max_length=255)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField(default=0)
    
    def __str__(self):
        return f"'{self.query_text}' ({self.results_count} results)"
    
    class Meta:
        verbose_name_plural = "Search queries"
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['query_text']),
        ]

class SalesMetric(models.Model):
    """Aggregated sales metrics for different time periods"""
    PERIOD_CHOICES = (
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    )
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    date = models.DateField()
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    order_count = models.IntegerField(default=0)
    refund_count = models.IntegerField(default=0)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.period_type.title()} metrics for {self.date}"
    
    class Meta:
        unique_together = ('period_type', 'date')
        indexes = [
            models.Index(fields=['period_type', 'date']),
        ]

class ProductPerformance(models.Model):
    """Track performance metrics for products"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='performance_metrics')
    date = models.DateField()
    view_count = models.IntegerField(default=0)
    cart_additions = models.IntegerField(default=0)
    purchase_count = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.product.name} performance on {self.date}"
    
    class Meta:
        unique_together = ('product', 'date')
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['product']),
        ]

class CustomerSegment(models.Model):
    """Customer segmentation data"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    criteria = models.JSONField(help_text="JSON representation of segment criteria")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
