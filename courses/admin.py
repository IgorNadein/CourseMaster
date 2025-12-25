from django.contrib import admin
from .models import Category, Course, Section, Lesson, Enrollment, LessonProgress, Review


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    fields = ['title', 'order']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['title', 'lesson_type', 'order', 'duration_minutes', 'is_preview']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'level', 'price', 'status', 'students_count', 'created_at']
    list_filter = ['status', 'level', 'category', 'is_free']
    search_fields = ['title', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [SectionInline]
    readonly_fields = ['students_count', 'average_rating', 'total_reviews', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'subtitle', 'description', 'instructor', 'category')
        }),
        ('Media', {
            'fields': ('thumbnail', 'preview_video')
        }),
        ('Details', {
            'fields': ('level', 'language', 'duration_hours')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'is_free')
        }),
        ('Content', {
            'fields': ('learning_outcomes', 'requirements', 'target_audience')
        }),
        ('Status', {
            'fields': ('status', 'published_at')
        }),
        ('Statistics', {
            'fields': ('students_count', 'average_rating', 'total_reviews', 'created_at', 'updated_at')
        }),
    )


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'created_at']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'section', 'lesson_type', 'order', 'duration_minutes', 'is_preview']
    list_filter = ['lesson_type', 'is_preview', 'section__course']
    search_fields = ['title', 'section__title']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'progress_percentage', 'completed']
    list_filter = ['completed', 'enrolled_at']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['enrolled_at']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['student__username', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']

