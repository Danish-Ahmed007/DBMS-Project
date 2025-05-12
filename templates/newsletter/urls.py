from django.urls import path
from .views import test_newsletter_view, subscribe_newsletter

urlpatterns = [
    path('test/', test_newsletter_view, name='test_newsletter'),
    path('subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
]
