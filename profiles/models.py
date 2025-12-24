from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Extended user profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    website = models.URLField(max_length=200, blank=True)
    
    # Role fields
    is_instructor = models.BooleanField(default=False, help_text='User can create and sell courses')
    is_student = models.BooleanField(default=True, help_text='User can enroll in courses')
    
    # Additional fields
    headline = models.CharField(max_length=200, blank=True, help_text='Professional headline (e.g., "Python Developer")')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s profile"
