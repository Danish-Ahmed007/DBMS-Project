"""
Middleware for tracking analytics data
"""
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
import re

from .services import record_page_view

class AnalyticsMiddleware(MiddlewareMixin):
    """
    Middleware for tracking page views and other analytics metrics
    """
    
    def process_request(self, request):
        # Exclude static files, admin, and common bot user agents
        path = request.path
        
        # Skip analytics tracking for static files, admin, etc.
        if re.match(r'^/(static|admin|media)/', path) or path == '/favicon.ico':
            return None
            
        # Skip analytics for API calls
        if path.startswith('/api/'):
            return None
        
        # Record page view
        try:
            record_page_view(request, path)
        except Exception:
            # Don't block the request if analytics fails
            pass
            
        return None
