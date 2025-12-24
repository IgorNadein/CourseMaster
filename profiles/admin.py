from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_instructor', 'is_student', 'location', 'created_at')
    search_fields = ('user__username', 'user__email', 'location', 'headline')
    list_filter = ('is_instructor', 'is_student', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('bio', 'headline', 'location', 'birth_date', 'website', 'avatar')
        }),
        ('Roles', {
            'fields': ('is_instructor', 'is_student')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
