from django.contrib import admin
from django.utils.html import format_html
from .models import (Category, Course, Section, Lesson, Enrollment, LessonProgress, Review, 
                     Quiz, Question, QuestionChoice, QuizAttempt, UserAnswer, Assignment, 
                     AssignmentSubmission, Certificate, LessonComment, PaymentMethod, Purchase, 
                     Payment, PromoCode, Refund, CourseMedia)


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


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student_name', 'course_title', 'issued_at']
    list_filter = ['issued_at']
    search_fields = ['certificate_number', 'student_name', 'course_title']
    readonly_fields = ['certificate_number', 'issued_at', 'student_name', 'course_title', 'instructor_name']
    
    fieldsets = (
        ('Certificate Info', {
            'fields': ('certificate_number', 'enrollment', 'issued_at')
        }),
        ('Snapshot Data', {
            'fields': ('student_name', 'course_title', 'instructor_name')
        }),
    )

# ============================================================
# PAYMENT ADMIN (Система платежей)
# ============================================================

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'is_active']
    list_filter = ['is_active', 'type']
    search_fields = ['name', 'description']


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'total_amount', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'payment_method']
    search_fields = ['student__username', 'course__title', 'transaction_id']
    readonly_fields = ['created_at', 'completed_at', 'refunded_at']
    
    fieldsets = (
        ('Purchase Info', {
            'fields': ('student', 'course', 'payment_method', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_amount', 'total_amount', 'promo_code')
        }),
        ('Payment Details', {
            'fields': ('transaction_id', 'created_at', 'completed_at')
        }),
        ('Refund', {
            'fields': ('refund_reason', 'refund_amount', 'refunded_at')
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'purchase', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['purchase__student__username', 'stripe_payment_intent_id', 'paypal_order_id']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    
    fieldsets = (
        ('Payment Info', {
            'fields': ('purchase', 'amount', 'currency', 'status')
        }),
        ('Stripe Data', {
            'fields': ('stripe_payment_intent_id', 'stripe_client_secret')
        }),
        ('PayPal Data', {
            'fields': ('paypal_order_id',)
        }),
        ('Yookassa Data', {
            'fields': ('yookassa_payment_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
        ('Error Handling', {
            'fields': ('error_message',)
        }),
    )


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_value', 'discount_type', 'is_active', 'current_uses', 'valid_until']
    list_filter = ['is_active', 'discount_type', 'valid_until']
    search_fields = ['code', 'description']
    readonly_fields = ['created_at', 'current_uses']
    filter_horizontal = ['applicable_courses']
    
    fieldsets = (
        ('Code Info', {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value')
        }),
        ('Limits', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Validity', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Courses', {
            'fields': ('applicable_courses',)
        }),
        ('Created', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['id', 'student', 'purchase', 'refund_amount', 'status', 'requested_at']
    list_filter = ['status', 'requested_at']
    search_fields = ['student__username', 'purchase__course__title', 'reason']
    readonly_fields = ['requested_at', 'processed_at']
    
    fieldsets = (
        ('Refund Request', {
            'fields': ('purchase', 'student', 'reason', 'status')
        }),
        ('Amount', {
            'fields': ('refund_amount',)
        }),
        ('Timeline', {
            'fields': ('requested_at', 'processed_at')
        }),
        ('Rejection', {
            'fields': ('rejection_reason',)
        }),
    )


# ============================================================
# MEDIA LIBRARY ADMIN (Медиа-библиотека)
# ============================================================

@admin.register(CourseMedia)
class CourseMediaAdmin(admin.ModelAdmin):
    list_display = ['thumbnail_preview', 'title', 'original_filename', 'course', 'media_type', 'file_size_display', 'created_at']
    list_filter = ['media_type', 'course', 'created_at']
    search_fields = ['title', 'original_filename', 'course__title', 'uploaded_by__username']
    readonly_fields = ['file_size', 'mime_type', 'width', 'height', 'duration_seconds', 'created_at', 'updated_at', 'file_preview']
    
    fieldsets = (
        ('Файл', {
            'fields': ('course', 'file', 'original_filename', 'file_preview')
        }),
        ('Метаданные', {
            'fields': ('title', 'description', 'media_type')
        }),
        ('Технические данные', {
            'fields': ('file_size', 'mime_type', 'width', 'height', 'duration_seconds')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def file_size_display(self, obj):
        return obj.file_size_display
    file_size_display.short_description = 'Размер'
    
    def thumbnail_preview(self, obj):
        if obj.is_image and obj.file:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.file.url)
        elif obj.is_video:
            return format_html('<i class="bi bi-film" style="font-size: 24px; color: #6c757d;"></i>')
        elif obj.is_document:
            return format_html('<i class="bi bi-file-earmark-text" style="font-size: 24px; color: #6c757d;"></i>')
        else:
            return format_html('<i class="bi bi-file" style="font-size: 24px; color: #6c757d;"></i>')
    thumbnail_preview.short_description = ''
    
    def file_preview(self, obj):
        if obj.is_image and obj.file:
            return format_html('<img src="{}" style="max-width: 300px; max-height: 200px;" />', obj.file.url)
        elif obj.is_video and obj.file:
            return format_html('<video src="{}" controls style="max-width: 300px;"></video>', obj.file.url)
        return 'Нет предпросмотра'
    file_preview.short_description = 'Предпросмотр'