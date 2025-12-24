from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re


class UserRegistrationForm(UserCreationForm):
    """Custom registration form with email and enhanced validation"""
    email = forms.EmailField(
        required=True,
        help_text='Required. Enter a valid email address.',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
        help_texts = {
            'username': '3-30 characters. Letters, digits and @/./+/-/_ only.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['password1'].help_text = 'Must be at least 8 characters with uppercase, lowercase, and number.'
        self.fields['password2'].help_text = 'Enter the same password for verification.'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check length
        if len(username) < 3 or len(username) > 30:
            raise ValidationError('Username must be between 3 and 30 characters.')
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        
        return email
    
    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        
        # Check minimum length
        if len(password) < 8:
            raise ValidationError('Password must contain at least 8 characters.')
        
        # Check for uppercase letter
        if not re.search(r'[A-Z]', password):
            raise ValidationError('Password must contain at least one uppercase letter.')
        
        # Check for lowercase letter
        if not re.search(r'[a-z]', password):
            raise ValidationError('Password must contain at least one lowercase letter.')
        
        # Check for digit
        if not re.search(r'\d', password):
            raise ValidationError('Password must contain at least one number.')
        
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match.")
        
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    """Custom login form that accepts username or email"""
    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    error_messages = {
        'invalid_login': 'Invalid username or password. Please try again.',
        'inactive': 'This account is inactive.',
    }
    
    def clean_username(self):
        username_or_email = self.cleaned_data.get('username')
        
        # Check if input is an email
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                return user.username
            except User.DoesNotExist:
                pass
        
        return username_or_email
