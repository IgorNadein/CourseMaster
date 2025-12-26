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
        # Context contains stats
        self.assertIn('total_students', response.context)
        self.assertIn('total_courses', response.context)
        self.assertIn('total_instructors', response.context)
    
    def test_home_page_content(self):
        """Test that home page contains key content"""
        response = self.client.get(self.home_url)
        
        # Check hero section (Russian)
        self.assertContains(response, 'CourseMaster')
    
    def test_home_page_links(self):
        """Test that home page contains important links"""
        response = self.client.get(self.home_url)
        
        # Check navigation is rendered (Russian)
        self.assertContains(response, 'Главная')
        self.assertContains(response, 'Курсы')
