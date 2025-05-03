from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    readonly_fields = ['product_name', 'product_price', 'quantity', 'subtotal']
    extra = 0
    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_date', 'status', 'status_badge', 'total_price', 'updated_at']
    list_filter = ['status', 'order_date']
    search_fields = ['user__username', 'id']
    readonly_fields = ['order_date', 'total_price']
    inlines = [OrderItemInline]
    list_editable = ['status']  # Now status is included in list_display
    actions = ['mark_as_processing', 'mark_as_accepted', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_completed', 'mark_as_cancelled']
    
    def status_badge(self, obj):
        """Display the status with a colored badge."""
        status_colors = {
            'Pending': 'warning',
            'Processing': 'info',
            'Accepted': 'primary',
            'Shipped': 'secondary',
            'Delivered': 'success',
            'Completed': 'success',
            'Cancelled': 'danger',
        }
        color = status_colors.get(obj.status, 'secondary')
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.status)
    
    status_badge.short_description = 'Status'
    
    def mark_as_processing(self, request, queryset):
        queryset.update(status='Processing')
    mark_as_processing.short_description = "Mark selected orders as Processing"
    
    def mark_as_accepted(self, request, queryset):
        queryset.update(status='Accepted')
    mark_as_accepted.short_description = "Mark selected orders as Accepted"
    
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='Shipped')
    mark_as_shipped.short_description = "Mark selected orders as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        queryset.update(status='Delivered')
    mark_as_delivered.short_description = "Mark selected orders as Delivered"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='Completed')
    mark_as_completed.short_description = "Mark selected orders as Completed"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='Cancelled')
    mark_as_cancelled.short_description = "Mark selected orders as Cancelled"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'product_price', 'quantity', 'subtotal']
    list_filter = ['order__status']
    search_fields = ['product_name']
