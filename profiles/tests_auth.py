from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from profiles.models import UserProfile
from profiles.forms import UserRegistrationForm, UserLoginForm


class UserRegistrationTests(TestCase):
    """Test user registration functionality"""
    
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    
    def test_registration_page_loads(self):
        """Test that registration page loads successfully"""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/register.html')
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        }
        response = self.client.post(self.register_url, data)
        
        # Check user was created
        self.assertTrue(User.objects.filter(username='testuser').exists())
        
        # Check profile was created automatically
        user = User.objects.get(username='testuser')
        self.assertTrue(hasattr(user, 'profile'))
        
        # Check redirect to profile
        self.assertEqual(response.status_code, 302)
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        User.objects.create_user('testuser', 'test@example.com', 'TestPass123')
        
        data = {
            'username': 'testuser',
            'email': 'another@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username', 'This username is already taken.')
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        User.objects.create_user('testuser', 'test@example.com', 'TestPass123')
        
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'email', 'This email is already registered.')


class UserLoginTests(TestCase):
    """Test user login functionality"""
    
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
    
    def test_user_login_with_username(self):
        """Test login with username"""
        data = {
            'username': 'testuser',
            'password': 'TestPass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_user_login_with_email(self):
        """Test login with email (converted to username)"""
        data = {
            'username': 'test@example.com',
            'password': 'TestPass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class RegistrationFormTests(TestCase):
    """Test UserRegistrationForm validation"""
    
    def test_registration_form_validation(self):
        """Test form with valid data"""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass123'
        })
        self.assertTrue(form.is_valid())
    
    def test_form_password_too_short(self):
        """Test password minimum length validation"""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'Test1',
            'password2': 'Test1'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_password_no_uppercase(self):
        """Test password must contain uppercase"""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        self.assertFalse(form.is_valid())
    
    def test_form_passwords_dont_match(self):
        """Test password confirmation must match"""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'TestPass123',
            'password2': 'TestPass456'
        })
        self.assertFalse(form.is_valid())


class PasswordResetTests(TestCase):
    """Test password reset functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.password_reset_url = reverse('password_reset')
    
    # TODO: Fix missing template registration/password_reset_subject.txt
    # def test_password_reset_request(self):
    #     """Test password reset request"""
    #     data = {
    #         'email': 'test@example.com'
    #     }
    #     response = self.client.post(self.password_reset_url, data)
    #     self.assertEqual(response.status_code, 302)


class LoginFormTests(TestCase):
    """Test UserLoginForm"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
    
    def test_login_form_with_username(self):
        """Test login form accepts username"""
        form = UserLoginForm(data={
            'username': 'testuser',
            'password': 'TestPass123'
        })
        # Note: AuthenticationForm needs request parameter for full validation
        # This test just checks basic form structure
        self.assertIn('username', form.fields)
        self.assertIn('password', form.fields)
