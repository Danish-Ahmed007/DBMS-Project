"""
Analytics services for processing and aggregating data
"""
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from django.db import transaction
from datetime import datetime, timedelta
import logging

from .models import SalesMetric, ProductPerformance, PageView, ProductView, SearchQuery
from orders.models import Order, OrderItem
from products.models import Product, Category

logger = logging.getLogger(__name__)

def record_page_view(request, page_url):
    """
    Record a page view event for analytics
    
    Args:
        request: The HTTP request object
        page_url: URL of the viewed page
    """
    try:
        # Extract user info if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Get session ID
        session_id = request.session.session_key
        
        # Get IP and user agent
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
            
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Create the page view record
        PageView.objects.create(
            user=user,
            page_url=page_url,
            session_id=session_id,
            ip_address=ip,
            user_agent=user_agent
        )
        
        return True
    except Exception as e:
        logger.error(f"Error recording page view: {str(e)}")
        return False

def record_product_view(request, product):
    """
    Record a product view event
    
    Args:
        request: The HTTP request object
        product: Product instance that was viewed
    """
    try:
        # Extract user info if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Get session ID
        session_id = request.session.session_key
        
        # Create the product view record
        ProductView.objects.create(
            user=user,
            product=product,
            session_id=session_id
        )
        
        return True
    except Exception as e:
        logger.error(f"Error recording product view: {str(e)}")
        return False

def record_search_query(request, query, results_count):
    """
    Record a search query and its results
    
    Args:
        request: The HTTP request object
        query: The search query string
        results_count: Number of search results
    """
    try:
        # Extract user info if authenticated
        user = request.user if request.user.is_authenticated else None
        
        # Create the search query record
        SearchQuery.objects.create(
            user=user,
            query_text=query,
            results_count=results_count
        )
        
        return True
    except Exception as e:
        logger.error(f"Error recording search query: {str(e)}")
        return False

@transaction.atomic
def aggregate_daily_sales_metrics():
    """
    Aggregate sales metrics for the previous day
    This should be run daily as a scheduled task
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    
    try:
        # Check if we already have metrics for yesterday
        if SalesMetric.objects.filter(period_type='daily', date=yesterday).exists():
            logger.info(f"Daily metrics for {yesterday} already exist, skipping aggregation.")
            return False
            
        # Get yesterday's orders
        yesterday_orders = Order.objects.filter(
            order_date__date=yesterday
        )
        
        # Calculate metrics
        total_sales = yesterday_orders.filter(status='Completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        order_count = yesterday_orders.count()
        
        # Create metrics record
        SalesMetric.objects.create(
            period_type='daily',
            date=yesterday,
            total_sales=total_sales,
            order_count=order_count,
            # Add more metrics as needed
        )
        
        logger.info(f"Daily sales metrics for {yesterday} successfully aggregated.")
        return True
    except Exception as e:
        logger.error(f"Error aggregating daily sales metrics: {str(e)}")
        return False

@transaction.atomic
def aggregate_weekly_sales_metrics():
    """
    Aggregate weekly sales metrics
    This should be run weekly as a scheduled task
    """
    # Last complete week (Monday to Sunday)
    today = timezone.now().date()
    days_since_monday = today.weekday()
    last_sunday = today - timedelta(days=days_since_monday + 1)
    last_monday = last_sunday - timedelta(days=6)
    
    try:
        # Check if we already have metrics for this week
        if SalesMetric.objects.filter(period_type='weekly', date=last_sunday).exists():
            logger.info(f"Weekly metrics for week ending {last_sunday} already exist, skipping.")
            return False
            
        # Get last week's orders
        weekly_orders = Order.objects.filter(
            order_date__date__gte=last_monday,
            order_date__date__lte=last_sunday
        )
        
        # Calculate metrics
        total_sales = weekly_orders.filter(status='Completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        order_count = weekly_orders.count()
        
        # Create metrics record (using Sunday as the date)
        SalesMetric.objects.create(
            period_type='weekly',
            date=last_sunday,
            total_sales=total_sales,
            order_count=order_count,
            # Add more metrics as needed
        )
        
        logger.info(f"Weekly sales metrics for week ending {last_sunday} successfully aggregated.")
        return True
    except Exception as e:
        logger.error(f"Error aggregating weekly sales metrics: {str(e)}")
        return False

@transaction.atomic
def aggregate_monthly_sales_metrics():
    """
    Aggregate monthly sales metrics
    This should be run monthly as a scheduled task
    """
    # Last complete month
    today = timezone.now().date()
    first_of_month = today.replace(day=1)
    last_month_end = first_of_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    
    try:
        # Check if we already have metrics for last month
        if SalesMetric.objects.filter(period_type='monthly', date=last_month_end).exists():
            logger.info(f"Monthly metrics for {last_month_end.strftime('%B %Y')} already exist, skipping.")
            return False
            
        # Get last month's orders
        monthly_orders = Order.objects.filter(
            order_date__date__gte=last_month_start,
            order_date__date__lte=last_month_end
        )
        
        # Calculate metrics
        total_sales = monthly_orders.filter(status='Completed').aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        order_count = monthly_orders.count()
        
        # Create metrics record (using last day of month as the date)
        SalesMetric.objects.create(
            period_type='monthly',
            date=last_month_end,
            total_sales=total_sales,
            order_count=order_count,
            # Add more metrics as needed
        )
        
        logger.info(f"Monthly sales metrics for {last_month_end.strftime('%B %Y')} successfully aggregated.")
        return True
    except Exception as e:
        logger.error(f"Error aggregating monthly sales metrics: {str(e)}")
        return False

@transaction.atomic
def aggregate_product_performance():
    """
    Aggregate product performance metrics for the previous day
    This should be run daily as a scheduled task
    """
    yesterday = timezone.now().date() - timedelta(days=1)
    
    try:
        # Process each product
        for product in Product.objects.all():
            # Check if we already have metrics for this product/date
            if ProductPerformance.objects.filter(product=product, date=yesterday).exists():
                continue
                
            # Count product views
            view_count = ProductView.objects.filter(
                product=product,
                view_time__date=yesterday
            ).count()
            
            # Count purchase data
            order_data = OrderItem.objects.filter(
                product=product,
                order__order_date__date=yesterday,
                order__status='Completed'
            ).aggregate(
                units=Sum('quantity'),
                revenue=Sum(F('product_price') * F('quantity'))
            )
            
            purchase_count = order_data['units'] or 0
            revenue = order_data['revenue'] or 0
            
            # TODO: Add cart additions when cart model is available
            cart_additions = 0
            
            # Create performance record
            ProductPerformance.objects.create(
                product=product,
                date=yesterday,
                view_count=view_count,
                cart_additions=cart_additions,
                purchase_count=purchase_count,
                revenue=revenue
            )
        
        logger.info(f"Product performance metrics for {yesterday} successfully aggregated.")
        return True
    except Exception as e:
        logger.error(f"Error aggregating product performance: {str(e)}")
        return False