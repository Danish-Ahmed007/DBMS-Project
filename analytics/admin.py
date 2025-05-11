from django.contrib import admin
from .models import (
    PageView, 
    ProductView, 
    SearchQuery, 
    SalesMetric, 
    ProductPerformance, 
    CustomerSegment
)

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'user', 'view_time', 'ip_address')
    list_filter = ('view_time',)
    search_fields = ('page_url', 'user__username', 'ip_address')
    date_hierarchy = 'view_time'

@admin.register(ProductView)
class ProductViewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'view_time')
    list_filter = ('view_time',)
    search_fields = ('product__name', 'user__username')
    date_hierarchy = 'view_time'

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ('query_text', 'user', 'results_count', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('query_text', 'user__username')
    date_hierarchy = 'timestamp'

@admin.register(SalesMetric)
class SalesMetricAdmin(admin.ModelAdmin):
    list_display = ('period_type', 'date', 'total_sales', 'order_count')
    list_filter = ('period_type', 'date')
    date_hierarchy = 'date'

@admin.register(ProductPerformance)
class ProductPerformanceAdmin(admin.ModelAdmin):
    list_display = ('product', 'date', 'view_count', 'purchase_count', 'revenue')
    list_filter = ('date',)
    search_fields = ('product__name',)
    date_hierarchy = 'date'

@admin.register(CustomerSegment)
class CustomerSegmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
