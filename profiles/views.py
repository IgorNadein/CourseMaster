from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .models import UserProfile
from .forms import UserRegistrationForm


def profile_view(request, username=None):
    """View a user's profile"""
    if username:
        user = get_object_or_404(User, username=username)
    else:
        if request.user.is_authenticated:
            user = request.user
        else:
            return redirect('login')
    
    profile = user.profile
    context = {
        'profile_user': user,
        'profile': profile,
    }
    return render(request, 'profiles/profile.html', context)


@login_required
def profile_edit(request):
    """Edit the current user's profile"""
    profile = request.user.profile
    
    if request.method == 'POST':
        # Update profile fields
        profile.bio = request.POST.get('bio', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.website = request.POST.get('website', '').strip()
        profile.headline = request.POST.get('headline', '').strip()
        
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        
        profile.save()
        
        # Update user fields
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'profile': profile,
    }
    return render(request, 'profiles/profile_edit.html', context)


def register_view(request):
    """Handle user registration"""
    # Redirect authenticated users
    if request.user.is_authenticated:
        return redirect('profile')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-login after registration
            login(request, user)
            messages.success(request, f'Welcome to CourseMaster, {user.username}! Your account has been created.')
            return redirect('profile')
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'registration/register.html', context)
