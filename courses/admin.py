from django.contrib import admin
from .models import Category, Course, Section, Lesson, Enrollment, LessonProgress, Review, Quiz, Question, QuestionChoice, QuizAttempt, UserAnswer, Assignment, AssignmentSubmission


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


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['enrollment', 'lesson', 'completed', 'completed_at', 'last_position']
    list_filter = ['completed', 'completed_at']
    search_fields = ['enrollment__student__username', 'lesson__title']
    readonly_fields = ['completed_at']


class QuestionChoiceInline(admin.TabularInline):
    model = QuestionChoice
    extra = 2
    fields = ['text', 'is_correct', 'order']


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['text', 'type', 'order', 'points']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'pass_percentage', 'created_at']
    list_filter = ['pass_percentage', 'created_at']
    search_fields = ['title', 'lesson__title']
    inlines = [QuestionInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'type', 'order', 'points']
    list_filter = ['type', 'quiz']
    search_fields = ['text', 'quiz__title']
    inlines = [QuestionChoiceInline]


@admin.register(QuestionChoice)
class QuestionChoiceAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct', 'order']
    list_filter = ['is_correct']
    search_fields = ['text', 'question__text']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'started_at', 'completed_at', 'percentage', 'is_passed']
    list_filter = ['is_passed', 'started_at']
    search_fields = ['student__username', 'quiz__title']
    readonly_fields = ['started_at', 'completed_at']


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct', 'points_earned', 'answered_at']
    list_filter = ['is_correct', 'answered_at']
    search_fields = ['attempt__student__username', 'question__text']
    readonly_fields = ['answered_at']


class AssignmentSubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    fields = ['student', 'submitted_at', 'status', 'points_earned', 'graded_at']
    readonly_fields = ['student', 'submitted_at', 'graded_at']
    can_delete = False


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'max_points', 'due_date', 'created_at']
    list_filter = ['due_date', 'created_at', 'lesson__section__course']
    search_fields = ['title', 'lesson__title', 'lesson__section__course__title']
    inlines = [AssignmentSubmissionInline]
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('lesson', 'title', 'description')
        }),
        ('Settings', {
            'fields': ('max_points', 'due_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'submitted_at', 'status', 'points_earned', 'is_late']
    list_filter = ['status', 'submitted_at', 'graded_at']
    search_fields = ['student__username', 'assignment__title', 'teacher_comment']
    readonly_fields = ['submitted_at', 'graded_at']
    
    fieldsets = (
        ('Submission', {
            'fields': ('assignment', 'student', 'submitted_at', 'submitted_file', 'submitted_text')
        }),
        ('Grading', {
            'fields': ('status', 'points_earned', 'teacher_comment', 'graded_at')
        }),
    )
    
    def is_late(self, obj):
        return obj.is_late
    is_late.boolean = True
    is_late.short_description = 'Late'

