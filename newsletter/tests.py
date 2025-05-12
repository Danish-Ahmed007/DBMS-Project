from django.test import TestCase, Client
from django.urls import reverse
from .models import NewsletterSubscription
import json

class NewsletterModelTests(TestCase):
    def test_newsletter_subscription_creation(self):
        """Test NewsletterSubscription model creation"""
        subscription = NewsletterSubscription.objects.create(email='test@example.com')
        self.assertEqual(subscription.email, 'test@example.com')
        self.assertTrue(subscription.is_active)
        self.assertIsNotNone(subscription.subscribed_at)

class NewsletterViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.subscribe_url = reverse('subscribe_newsletter')
        self.test_page_url = reverse('test_newsletter')
    
    def test_newsletter_test_page_loads(self):
        """Test that the newsletter test page loads correctly"""
        response = self.client.get(self.test_page_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsletter/test_subscription.html')
    
    def test_subscription_with_valid_email(self):
        """Test subscription with valid email"""
        data = {'email': 'new_user@example.com'}
        response = self.client.post(
            self.subscribe_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertEqual(NewsletterSubscription.objects.count(), 1)
    
    def test_subscription_with_duplicate_email(self):
        """Test subscription with duplicate email"""
        # Create subscription first
        NewsletterSubscription.objects.create(email='duplicate@example.com')
        
        # Try to subscribe again with the same email
        data = {'email': 'duplicate@example.com'}
        response = self.client.post(
            self.subscribe_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertEqual(NewsletterSubscription.objects.count(), 1)
    
    def test_reactivate_subscription(self):
        """Test reactivation of inactive subscription"""
        # Create inactive subscription
        sub = NewsletterSubscription.objects.create(email='inactive@example.com')
        sub.is_active = False
        sub.save()
        
        # Try to subscribe again with the same email
        data = {'email': 'inactive@example.com'}
        response = self.client.post(
            self.subscribe_url, 
            json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        
        # Verify subscription is now active
        sub.refresh_from_db()
        self.assertTrue(sub.is_active)
