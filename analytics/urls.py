from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('sales/', views.sales_analysis, name='sales_analysis'),
    path('products/', views.product_analytics, name='product_analytics'),
    path('customers/', views.customer_analytics, name='customer_analytics'),
    path('fraud/', views.fraud_analytics, name='fraud_analytics'),
    
    # API endpoints for chart data
    path('api/sales-chart/', views.api_sales_chart_data, name='api_sales_chart'),
]