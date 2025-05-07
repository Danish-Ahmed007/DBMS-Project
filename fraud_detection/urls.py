from django.urls import path
from . import views

urlpatterns = [
    # User-facing URLs
    path('verification/<uuid:confirmation_key>/', views.verification_required_view, name='verification_required'),
    path('confirm/<uuid:confirmation_key>/', views.confirm_transaction, name='confirm_transaction'),
    
    # Admin URLs
    path('dashboard/', views.fraud_dashboard, name='fraud_dashboard'),
    path('export-data/', views.export_transaction_data, name='export_transaction_data'),
]
