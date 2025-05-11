"""
Signals for analytics data tracking
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
import logging

from orders.models import Order, OrderItem
from .models import ProductPerformance, SalesMetric
from .services import aggregate_daily_sales_metrics, aggregate_product_performance

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Order)
def update_sales_metrics(sender, instance, created, **kwargs):
    """
    When an order is saved, update sales metrics
    """
    if not created and instance.status == 'Completed':
        # Order was just completed, update metrics
        try:
            # We'll use this as a trigger to update metrics
            # Schedule this as an async task in a real-world scenario
            transaction.on_commit(lambda: aggregate_daily_sales_metrics())
        except Exception as e:
            logger.error(f"Error updating sales metrics: {str(e)}")

@receiver(post_save, sender=OrderItem)
def update_product_performance(sender, instance, created, **kwargs):
    """
    When an order item is saved, update product performance metrics
    """
    if instance.product and instance.order.status == 'Completed':
        try:
            # Update product performance metrics
            # Schedule this as an async task in a real-world scenario
            transaction.on_commit(lambda: aggregate_product_performance())
        except Exception as e:
            logger.error(f"Error updating product performance: {str(e)}")
