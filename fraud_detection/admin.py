from django.contrib import admin
from django.utils import timezone
from django.urls import reverse
from django.utils.html import format_html
import json
from .models import TransactionData, FraudDetectionLog, FraudConfirmation

@admin.register(TransactionData)
class TransactionDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'order_total', 'location_match', 'transaction_time', 'is_first_purchase']
    list_filter = ['is_first_purchase', 'transaction_time']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['transaction_time']
    
    def location_match(self, obj):
        """Display if registration and confirmed locations match."""
        matches = obj.confirmed_location == obj.registration_location
        return format_html(
            '<span style="color: {};">{}</span>',
            'green' if matches else 'red',
            'Match' if matches else 'Mismatch'
        )
    
    location_match.short_description = 'Location Match'

@admin.register(FraudDetectionLog)
class FraudDetectionLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_link', 'is_flagged', 'risk_score', 'detection_time', 'display_reasons']
    list_filter = ['is_flagged', 'detection_time', 'risk_score']
    readonly_fields = ['detection_time']
    
    def transaction_link(self, obj):
        """Create a link to the related transaction."""
        url = reverse('admin:fraud_detection_transactiondata_change', args=[obj.transaction.id])
        return format_html('<a href="{}">{}</a>', url, f"Transaction #{obj.transaction.id}")
    
    transaction_link.short_description = 'Transaction'
    
    def display_reasons(self, obj):
        """Display the flag reasons in a readable format."""
        if not obj.flag_reasons or 'reasons' not in obj.flag_reasons:
            return '-'
        reasons = obj.flag_reasons['reasons']
        if not reasons:
            return '-'
        return format_html('<br>'.join(reasons[:2]) + ('...' if len(reasons) > 2 else ''))
    
    display_reasons.short_description = 'Flag Reasons'

@admin.register(FraudConfirmation)
class FraudConfirmationAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_link', 'is_confirmed', 'confirmation_status', 'created_at']
    list_filter = ['is_confirmed', 'created_at', 'expiry_time']
    readonly_fields = ['confirmation_key', 'created_at']
    actions = ['extend_expiry_time']
    
    def transaction_link(self, obj):
        """Create a link to the related transaction."""
        url = reverse('admin:fraud_detection_transactiondata_change', args=[obj.transaction.id])
        return format_html('<a href="{}">{}</a>', url, f"Transaction #{obj.transaction.id}")
    
    transaction_link.short_description = 'Transaction'
    
    def confirmation_status(self, obj):
        """Display confirmation status with color coding."""
        if obj.is_confirmed:
            return format_html('<span style="color: green;">Confirmed</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">Expired</span>')
        else:
            return format_html('<span style="color: orange;">Pending</span>')
    
    confirmation_status.short_description = 'Status'
    
    def extend_expiry_time(self, request, queryset):
        """Action to extend expiry time by 30 minutes."""
        for confirmation in queryset:
            if not confirmation.is_confirmed and confirmation.is_expired:
                confirmation.expiry_time = timezone.now() + timezone.timedelta(minutes=30)
                confirmation.save()
        self.message_user(request, f"Extended expiry time for {queryset.count()} confirmations.")
    
    extend_expiry_time.short_description = "Extend expiry time by 30 minutes"