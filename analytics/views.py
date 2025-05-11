from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q, Min
from django.http import JsonResponse
from datetime import datetime, timedelta
import json

from .models import SalesMetric, ProductPerformance, PageView, ProductView, SearchQuery
from products.models import Product, Category
from orders.models import Order, OrderItem
from fraud_detection.models import FraudDetectionLog, TransactionData

def is_admin(user):
    """Check if user is staff/admin"""
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def analytics_dashboard(request):
    """Main analytics dashboard showing key metrics"""
    # Get date range from request parameters or use default (last 30 days)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Get sales metrics
    total_revenue = Order.objects.filter(order_date__date__gte=date_from, status='Completed').aggregate(
        total=Sum('total_price')
    )['total'] or 0
    
    # Get order metrics
    order_count = Order.objects.filter(order_date__date__gte=date_from).count()
    avg_order_value = total_revenue / order_count if order_count > 0 else 0
    
    # Get daily sales data for chart
    daily_sales = Order.objects.filter(order_date__date__gte=date_from).values(
        'order_date__date'
    ).annotate(
        revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('order_date__date')
    
    # Format chart data
    chart_labels = [item['order_date__date'].strftime('%Y-%m-%d') for item in daily_sales]
    chart_revenue_data = [float(item['revenue']) if item['revenue'] else 0 for item in daily_sales]
    chart_order_data = [item['count'] for item in daily_sales]
    
    # Get top products by revenue
    top_products = OrderItem.objects.filter(
        order__order_date__date__gte=date_from,
        order__status='Completed'
    ).values(
        'product_name'
    ).annotate(
        revenue=Sum(F('product_price') * F('quantity')),
        units_sold=Sum('quantity')
    ).order_by('-revenue')[:5]
    
    # Get fraud metrics
    fraud_flags = FraudDetectionLog.objects.filter(
        detection_time__date__gte=date_from, 
        is_flagged=True
    ).count()
    
    fraud_rate = (fraud_flags / order_count * 100) if order_count > 0 else 0
    
    context = {
        'total_revenue': total_revenue,
        'order_count': order_count,
        'avg_order_value': avg_order_value,
        'fraud_flags': fraud_flags,
        'fraud_rate': fraud_rate,
        'top_products': top_products,
        'chart_labels': json.dumps(chart_labels),
        'chart_revenue_data': json.dumps(chart_revenue_data),
        'chart_order_data': json.dumps(chart_order_data),
        'days': days,
    }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def sales_analysis(request):
    """Detailed sales analytics view"""
    # Get date range from request parameters or use default (last 30 days)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Get sales by category
    sales_by_category = OrderItem.objects.filter(
        order__order_date__date__gte=date_from,
        order__status='Completed',
        product__isnull=False
    ).values(
        'product__category__name'
    ).annotate(
        revenue=Sum(F('product_price') * F('quantity')),
        units=Sum('quantity')
    ).order_by('-revenue')
    
    # Calculate percentages for the template to avoid CSS validation errors
    total_revenue = sum(item['revenue'] for item in sales_by_category) if sales_by_category else 0
    for item in sales_by_category:
        if total_revenue > 0:
            item['percentage'] = round((item['revenue'] / total_revenue) * 100, 0)
        else:
            item['percentage'] = 0
    
    # Get sales by payment method (if available)
    # Note: This assumes you have payment information in orders
    # sales_by_payment = Order.objects.filter(
    #     order_date__date__gte=date_from,
    #     status='Completed'
    # ).values('payment_method').annotate(
    #     revenue=Sum('total_price'),
    #     count=Count('id')
    # ).order_by('-revenue')
    
    # Get sales by day of week
    sales_by_dow = Order.objects.filter(
        order_date__date__gte=date_from,
        status='Completed'
    ).values(
        'order_date__week_day'
    ).annotate(
        revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('order_date__week_day')
    
    # Convert day of week numbers to names
    dow_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for item in sales_by_dow:
        # Django uses 1-7 for week days where 1 is Sunday, so convert to 0-6 where 0 is Monday
        item['day_name'] = dow_names[(item['order_date__week_day'] - 2) % 7]
    
    # Get hourly distribution of orders
    sales_by_hour = Order.objects.filter(
        order_date__date__gte=date_from,
    ).values(
        'order_date__hour'
    ).annotate(
        revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('order_date__hour')
      # Format data for JavaScript
    category_names = [cat.get('product__category__name', 'Unknown') or 'Unknown' 
                      for cat in sales_by_category]
    category_revenue = [float(cat.get('revenue', 0) or 0) for cat in sales_by_category]
    
    dow_names = [item['day_name'] for item in sales_by_dow]
    dow_revenue = [float(item['revenue'] or 0) for item in sales_by_dow]
    dow_orders = [item['count'] for item in sales_by_dow]
    
    # Process hourly data
    hour_numbers = [item['order_date__hour'] for item in sales_by_hour]
    hour_revenue = [float(item['revenue'] or 0) for item in sales_by_hour]
    hour_orders = [item['count'] for item in sales_by_hour]
    
    context = {
        'sales_by_category': sales_by_category,
        # 'sales_by_payment': sales_by_payment,
        'sales_by_dow': sales_by_dow,
        'sales_by_hour': sales_by_hour,
        'days': days,
        
        # JSON serialized data for JavaScript
        'category_names_json': json.dumps(category_names),
        'category_revenue_json': json.dumps(category_revenue),
        'dow_names_json': json.dumps(dow_names),
        'dow_revenue_json': json.dumps(dow_revenue),
        'dow_orders_json': json.dumps(dow_orders),
        'hour_numbers_json': json.dumps(hour_numbers),
        'hour_revenue_json': json.dumps(hour_revenue),
        'hour_orders_json': json.dumps(hour_orders),
    }
    
    return render(request, 'analytics/sales_analysis.html', context)

@login_required
@user_passes_test(is_admin)
def product_analytics(request):
    """Product performance analytics view"""
    # Get date range from request parameters or use default (last 30 days)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Get top selling products
    top_sellers = OrderItem.objects.filter(
        order__order_date__date__gte=date_from,
        order__status='Completed'
    ).values(
        'product_name', 
        'product__id'
    ).annotate(
        units_sold=Sum('quantity'),
        revenue=Sum(F('product_price') * F('quantity'))
    ).order_by('-units_sold')[:10]
    
    # Get most viewed products
    most_viewed = ProductView.objects.filter(
        view_time__date__gte=date_from
    ).values(
        'product__name',
        'product__id'
    ).annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:10]
    
    # Get conversion rate data (views to purchases)
    product_conversions = []
    for product in Product.objects.all()[:20]:  # Limit to avoid performance issues
        views = ProductView.objects.filter(
            product=product,
            view_time__date__gte=date_from
        ).count()
        
        orders = OrderItem.objects.filter(
            product=product,
            order__order_date__date__gte=date_from,
            order__status='Completed'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        if views > 0:
            conversion_rate = (orders / views) * 100
        else:
            conversion_rate = 0
            
        product_conversions.append({
            'name': product.name,
            'views': views,
            'orders': orders,
            'conversion_rate': conversion_rate
        })
    
    # Sort by conversion rate
    product_conversions.sort(key=lambda x: x['conversion_rate'], reverse=True)
      # Format data for JavaScript
    product_names = [product['name'] for product in product_conversions[:10]]
    conversion_rates = [product['conversion_rate'] for product in product_conversions[:10]]
    product_views = [product['views'] for product in product_conversions[:10]]
    product_orders = [product['orders'] for product in product_conversions[:10]]
    
    context = {
        'top_sellers': top_sellers,
        'most_viewed': most_viewed,
        'product_conversions': product_conversions[:10],  # Top 10 by conversion
        'days': days,
        
        # JSON serialized data for JavaScript
        'product_names_json': json.dumps(product_names),
        'conversion_rates_json': json.dumps(conversion_rates),
        'product_views_json': json.dumps(product_views),
        'product_orders_json': json.dumps(product_orders),
    }
    
    return render(request, 'analytics/product_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def customer_analytics(request):
    """Customer analytics view"""
    # Get date range from request parameters or use default (last 30 days)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Get top customers by order value
    top_customers = Order.objects.filter(
        order_date__date__gte=date_from,
        status='Completed'
    ).values(
        'user__username',
        'user__id',
        'user__email'
    ).annotate(
        order_count=Count('id'),
        total_spent=Sum('total_price')
    ).order_by('-total_spent')[:10]
    
    # Get customer locations distribution (if location data is available)
    locations = Order.objects.filter(
        order_date__date__gte=date_from,
    ).values(
        'user__location'
    ).annotate(
        count=Count('id'),
        revenue=Sum('total_price')
    ).order_by('-count')
    
    # Get new vs returning customer split
    # This is a simplified approach, it counts users who made their first order in the selected period
    all_user_orders = Order.objects.values('user').annotate(
        first_order_date=Min('order_date'),
        order_count=Count('id')
    )
    
    new_customers = sum(1 for user in all_user_orders 
                     if user['first_order_date'].date() >= date_from)
    returning_customers = sum(1 for user in all_user_orders
                           if user['first_order_date'].date() < date_from
                           and user['order_count'] > 1)
    
    # Calculate approximate customer lifetime value
    # This is a simplified calculation
    customer_ltv = Order.objects.filter(
        status='Completed'
    ).values(
        'user'
    ).annotate(
        total_spent=Sum('total_price'),
        order_count=Count('id')
    ).aggregate(
        avg_total=Avg('total_spent'),
        avg_orders=Avg('order_count')
    )
    
    avg_customer_value = customer_ltv.get('avg_total', 0) or 0
      # Format location data for JavaScript
    location_names = [loc.get('user__location', 'Unknown') or 'Unknown' for loc in locations]
    location_counts = [loc['count'] for loc in locations]
    
    context = {
        'top_customers': top_customers,
        'locations': locations,
        'new_customers': new_customers,
        'returning_customers': returning_customers,
        'avg_customer_value': avg_customer_value,
        'days': days,
        
        # JSON serialized data for JavaScript
        'location_names_json': json.dumps(location_names),
        'location_counts_json': json.dumps(location_counts),
    }
    
    return render(request, 'analytics/customer_analytics.html', context)

@login_required
@user_passes_test(is_admin)
def fraud_analytics(request):
    """Fraud analytics view"""
    # Get date range from request parameters or use default (last 30 days)
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    # Get overall fraud metrics
    total_transactions = TransactionData.objects.filter(
        transaction_time__date__gte=date_from
    ).count()
    
    flagged_transactions = FraudDetectionLog.objects.filter(
        detection_time__date__gte=date_from,
        is_flagged=True
    ).count()
    
    fraud_rate = (flagged_transactions / total_transactions * 100) if total_transactions > 0 else 0
    
    # Get risk score distribution
    risk_distribution = FraudDetectionLog.objects.filter(
        detection_time__date__gte=date_from
    ).values(
        'risk_score'
    ).annotate(
        count=Count('id')
    ).order_by('risk_score')
    
    # Analyze common fraud flags
    fraud_flags = []
    for log in FraudDetectionLog.objects.filter(
        detection_time__date__gte=date_from,
        is_flagged=True
    )[:100]:  # Limit to avoid performance issues
        if log.flag_reasons and 'reasons' in log.flag_reasons:
            for reason in log.flag_reasons['reasons']:
                fraud_flags.append(reason)
    
    # Count occurrences of each flag
    flag_counts = {}
    for flag in fraud_flags:
        flag_counts[flag] = flag_counts.get(flag, 0) + 1
    
    # Convert to list and sort
    flag_summary = [{'reason': reason, 'count': count} 
                   for reason, count in flag_counts.items()]
    flag_summary.sort(key=lambda x: x['count'], reverse=True)
      # Format data for JavaScript
    risk_scores = [item['risk_score'] for item in risk_distribution]
    risk_counts = [item['count'] for item in risk_distribution]
    
    flag_reasons = [flag['reason'] for flag in flag_summary[:10]]
    flag_counts = [flag['count'] for flag in flag_summary[:10]]
    
    context = {
        'total_transactions': total_transactions,
        'flagged_transactions': flagged_transactions,
        'fraud_rate': fraud_rate,
        'risk_distribution': risk_distribution,
        'flag_summary': flag_summary[:10],  # Top 10 reasons
        'days': days,
        
        # JSON serialized data for JavaScript
        'risk_scores_json': json.dumps(risk_scores),
        'risk_counts_json': json.dumps(risk_counts),
        'flag_reasons_json': json.dumps(flag_reasons),
        'flag_counts_json': json.dumps(flag_counts),
    }
    
    return render(request, 'analytics/fraud_analytics.html', context)

# API endpoints for chart data
@login_required
@user_passes_test(is_admin)
def api_sales_chart_data(request):
    """API endpoint to get sales chart data"""
    days = int(request.GET.get('days', 30))
    date_from = timezone.now().date() - timedelta(days=days)
    
    daily_sales = Order.objects.filter(order_date__date__gte=date_from).values(
        'order_date__date'
    ).annotate(
        revenue=Sum('total_price'),
        count=Count('id')
    ).order_by('order_date__date')
    
    # Format data for charts
    chart_data = {
        'labels': [item['order_date__date'].strftime('%Y-%m-%d') for item in daily_sales],
        'revenue': [float(item['revenue'] or 0) for item in daily_sales],
        'orders': [item['count'] for item in daily_sales],
    }
    
    return JsonResponse(chart_data)
