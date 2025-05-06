from django.db import models
from django.conf import settings
import uuid
import json

class TransactionData(models.Model):
    """
    Store metadata about each checkout attempt for fraud detection analysis
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    confirmed_location = models.CharField(max_length=100, help_text="Location confirmed during checkout")
    registration_location = models.CharField(max_length=100, help_text="Location from user profile")
    device_info = models.JSONField(null=True, blank=True, help_text="Information about user device")
    transaction_time = models.DateTimeField(auto_now_add=True)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    is_first_purchase = models.BooleanField(default=False)
    user_order_average = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"Transaction {self.id} by {self.user.username} for ${self.order_total}"

class FraudDetectionLog(models.Model):
    """
    Track fraud detection checks with reasons why transactions were flagged
    """
    transaction = models.OneToOneField(TransactionData, on_delete=models.CASCADE, related_name='fraud_log')
    is_flagged = models.BooleanField(default=False)
    flag_reasons = models.JSONField(default=dict, help_text="Reasons the transaction was flagged")
    detection_time = models.DateTimeField(auto_now_add=True)
    risk_score = models.IntegerField(default=0, help_text="Higher values indicate higher risk")
    
    def __str__(self):
        return f"Fraud check for Transaction {self.transaction.id} - {'FLAGGED' if self.is_flagged else 'PASSED'}"

    def add_flag_reason(self, reason):
        """Add a reason why transaction was flagged"""
        reasons = self.flag_reasons.copy() if self.flag_reasons else {}
        if 'reasons' not in reasons:
            reasons['reasons'] = []
        reasons['reasons'].append(reason)
        self.flag_reasons = reasons
        self.save()

class FraudConfirmation(models.Model):
    """
    Store pending transactions requiring user confirmation
    """
    transaction = models.OneToOneField(TransactionData, on_delete=models.CASCADE, related_name='confirmation')
    confirmation_key = models.UUIDField(default=uuid.uuid4, editable=False)
    is_confirmed = models.BooleanField(default=False)
    expiry_time = models.DateTimeField()
    cart_snapshot = models.JSONField(default=dict, help_text="JSON representation of cart at time of transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Confirmation for Transaction {self.transaction.id} - {'Confirmed' if self.is_confirmed else 'Pending'}"
    
    @property
    def is_expired(self):
        """Check if the confirmation link has expired"""
        from django.utils import timezone
        return self.expiry_time < timezone.now()
