from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('history/', views.order_history_view, name='order_history'),
    path('detail/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # Staff-only URLs for order management
    path('management/', views.order_management_view, name='order_management'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_order_status'),
]