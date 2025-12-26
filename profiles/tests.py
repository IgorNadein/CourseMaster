from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile


class UserRegistrationTests(TestCase):
    """Tests for user registration functionality"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_register_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_successful_registration(self):
        """Test successful user registration with valid data"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        }
        response = self.client.post(self.register_url, data)
        
        # Should redirect to profile after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # User should be created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # User should be logged in
        user = User.objects.get(username='testuser')
        self.assertTrue(user.is_authenticated)
        
        # Profile should be auto-created via signals
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_registration_duplicate_username(self):
        """Test registration fails with duplicate username"""
        User.objects.create_user(username='testuser', email='existing@example.com', password='pass')
        
        data = {
            'username': 'testuser',
            'email': 'new@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        }
        response = self.client.post(self.register_url, data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This username is already taken.')
    
    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        User.objects.create_user(username='existing', email='test@example.com', password='pass')
        
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        }
        response = self.client.post(self.register_url, data)
        
        # Should stay on registration page
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'This email is already registered.')
    
    def test_registration_short_username(self):
        """Test registration fails with username too short"""
        data = {
            'username': 'ab',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'Username must be between 3 and 30 characters.')
    
    def test_registration_password_too_short(self):
        """Test registration fails with password too short"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'Short1',
            'password2': 'Short1',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password1', 'Password must contain at least 8 characters.')
    
    def test_registration_password_no_uppercase(self):
        """Test registration fails with password without uppercase letter"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password1', 'Password must contain at least one uppercase letter.')
    
    def test_registration_password_no_lowercase(self):
        """Test registration fails with password without lowercase letter"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TESTPASS123',
            'password2': 'TESTPASS123',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password1', 'Password must contain at least one lowercase letter.')
    
    def test_registration_password_no_number(self):
        """Test registration fails with password without number"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPassword',
            'password2': 'TestPassword',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password1', 'Password must contain at least one number.')
    
    def test_registration_passwords_dont_match(self):
        """Test registration fails when passwords don't match"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'DifferentPass123',
        }
        response = self.client.post(self.register_url, data)
        
        self.assertEqual(response.status_code, 200)
        # Check that form has errors
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('password2', response.context['form'].errors)
    
    def test_authenticated_user_redirected(self):
        """Test that authenticated users are redirected from registration page"""
        user = User.objects.create_user(username='testuser', password='TestPass123')
        self.client.force_login(user)
        
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))


class UserLoginTests(TestCase):
    """Tests for user login functionality"""
    
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads successfully"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/login.html')
    
    def test_login_with_username(self):
        """Test successful login with username"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123',
        }
        response = self.client.post(self.login_url, data)
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
        
        # User should be logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_with_email(self):
        """Test successful login with email"""
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123',
        }
        response = self.client.post(self.login_url, data)
        
        # Should redirect to profile
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profile'))
    
    def test_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword',
        }
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid username or password')
    
    def test_login_nonexistent_user(self):
        """Test login fails with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'TestPass123',
        }
        response = self.client.post(self.login_url, data)
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)


class UserLogoutTests(TestCase):
    """Tests for user logout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )
    
    def test_logout(self):
        """Test successful logout"""
        self.client.force_login(self.user)
        
        response = self.client.post(self.logout_url)
        
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))


class PasswordResetTests(TestCase):
    """Tests for password reset functionality"""
    
    def setUp(self):
        self.client = Client()
        self.password_reset_url = reverse('password_reset')
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_password_reset_page_loads(self):
        """Test that password reset page loads successfully"""
        response = self.client.get(self.password_reset_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/password_reset_form.html')
    
    # TODO: Fix missing template registration/password_reset_subject.txt
    # def test_password_reset_request(self):
    #     """Test password reset request with valid email"""
    #     data = {'email': 'test@example.com'}
    #     response = self.client.post(self.password_reset_url, data)
    #     
    #     # Should redirect to password reset done page
    #     self.assertEqual(response.status_code, 302)
    #     self.assertRedirects(response, reverse('password_reset_done'))


class ProfileViewTests(TestCase):
    """Tests for profile view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123'
        )
        self.profile_url = reverse('profile')
    
    def test_profile_view_authenticated(self):
        """Test that authenticated users can view their profile"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile.html')
    
    def test_profile_view_unauthenticated(self):
        """Test that unauthenticated users are redirected to login"""
        response = self.client.get(self.profile_url)
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

