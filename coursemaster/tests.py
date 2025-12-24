from django.test import TestCase, Client
from django.urls import reverse


class HomeViewTests(TestCase):
    """Tests for home landing page view"""
    
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('home')
    
    def test_home_page_loads(self):
        """Test that home page loads successfully"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_page_context(self):
        """Test that home page has correct context data"""
        response = self.client.get(self.home_url)
        self.assertEqual(response.context['total_students'], 10000)
        self.assertEqual(response.context['total_courses'], 500)
        self.assertEqual(response.context['total_instructors'], 200)
    
    def test_home_page_content(self):
        """Test that home page contains key content"""
        response = self.client.get(self.home_url)
        
        # Check hero section
        self.assertContains(response, 'Learn Without Limits')
        self.assertContains(response, 'Transform your career')
        
        # Check features section
        self.assertContains(response, 'Expert Instructors')
        self.assertContains(response, 'Flexible Learning')
        self.assertContains(response, 'Lifetime Access')
        self.assertContains(response, 'Community Support')
        
        # Check courses section
        self.assertContains(response, 'Popular Courses')
        self.assertContains(response, 'Complete Python Bootcamp')
        self.assertContains(response, 'Web Development Masterclass')
        
        # Check stats section
        self.assertContains(response, '10000')
        self.assertContains(response, '500')
        self.assertContains(response, '200')
        
        # Check CTA section
        self.assertContains(response, 'Become an Instructor')
        
        # Check footer
        self.assertContains(response, 'CourseMaster. All rights reserved')
    
    def test_home_page_links(self):
        """Test that home page contains important links"""
        response = self.client.get(self.home_url)
        
        # Check CTA buttons
        self.assertContains(response, 'Get Started')
        self.assertContains(response, 'Browse Courses')
        
        # Check navigation is rendered (inherited from base template)
        self.assertContains(response, 'Home')
        self.assertContains(response, 'Login')
        self.assertContains(response, 'Sign Up')
