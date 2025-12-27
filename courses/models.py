from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon class")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = 'category'
            self.slug = base_slug
            
            # Проверить уникальность slug
            counter = 1
            while Category.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Course(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликован'),
        ('archived', 'Архив'),
    ]
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True, help_text="Short catchy description")
    description = models.TextField(blank=True, help_text="Full course description")
    
    # Instructor & Category
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='courses_taught')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    # Media
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    preview_video = models.URLField(blank=True, help_text="YouTube or Vimeo URL")
    
    # Course Details
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='beginner')
    language = models.CharField(max_length=50, default='English')
    duration_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Total course duration in hours")
    
    # Pricing
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    is_free = models.BooleanField(default=False)
    
    # What students will learn
    learning_outcomes = models.TextField(help_text="One per line", blank=True)
    requirements = models.TextField(help_text="Prerequisites, one per line", blank=True)
    target_audience = models.TextField(help_text="Who is this course for, one per line", blank=True)
    
    # Status & Timestamps
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Stats (computed fields, can be cached)
    students_count = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    total_reviews = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', 'status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            
            # Если slug пустой (например, только кириллица)
            if not base_slug:
                import uuid
                base_slug = f"course-{uuid.uuid4().hex[:8]}"
            
            self.slug = base_slug
            
            # Проверить уникальность slug
            counter = 1
            while Course.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def current_price(self):
        """Return discount price if available, else regular price"""
        if self.is_free:
            return 0
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price
    
    @property
    def has_discount(self):
        """Check if course has active discount"""
        return self.discount_price and self.discount_price < self.price


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Видео'),
        ('article', 'Статья'),
        ('quiz', 'Тест'),
        ('assignment', 'Задание'),
    ]
    
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='video')
    order = models.PositiveIntegerField(default=0)
    
    # Content
    content = models.TextField(blank=True, help_text="Article content or lesson notes")
    video_url = models.URLField(blank=True, help_text="Video URL (YouTube, Vimeo, etc.)")
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Lesson duration in minutes")
    
    # Resources
    attachment = models.FileField(upload_to='courses/attachments/', blank=True, null=True)
    
    # Access
    is_preview = models.BooleanField(default=False, help_text="Can be viewed without enrollment")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['section', 'order']
    
    def __str__(self):
        return f"{self.section.title} - {self.title}"


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title}"


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)
    last_position = models.PositiveIntegerField(default=0, help_text="Video position in seconds")
    
    class Meta:
        unique_together = ['enrollment', 'lesson']
        ordering = ['lesson__order']
    
    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title}"


class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        choices=[(i, i) for i in range(1, 6)],
        help_text="Rating from 1 to 5"
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['course', 'student']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.rating}★)"


class Quiz(models.Model):
    """Quiz attached to a specific lesson"""
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    pass_percentage = models.PositiveIntegerField(default=50, help_text="Минимальный % для прохождения")
    time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Лимит времени на тест в минутах")
    attempts_limit = models.PositiveIntegerField(default=3, help_text="Максимальное количество попыток")
    shuffle_questions = models.BooleanField(default=False)
    show_answers = models.BooleanField(default=True, help_text="Показывать правильные ответы после завершения")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return f"Quiz: {self.lesson.title}"


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('multiple', 'Множественный выбор'),
        ('single', 'Одиночный выбор'),
        ('true_false', 'Правда/Ложь'),
        ('text', 'Текстовый ответ'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='single')
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    points = models.PositiveIntegerField(default=1, help_text="Баллы за правильный ответ")
    explanation = models.TextField(blank=True, help_text="Объяснение, показываемое после ответа")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['quiz', 'order']
    
    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}: {self.text[:50]}"


class QuestionChoice(models.Model):
    """Answer choices for multiple/single choice questions"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order']
        unique_together = ['question', 'order']
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:30]}"
    
    def save(self, *args, **kwargs):
        """
        Для вопросов с одиночным выбором (single/true_false):
        если установить is_correct=True, автоматически снимаем флаг с других вариантов
        """
        if self.is_correct and self.question.type in ['single', 'true_false']:
            # Снять is_correct со всех остальных вариантов этого вопроса
            self.question.choices.exclude(pk=self.pk).update(is_correct=False)
        
        super().save(*args, **kwargs)


class QuizAttempt(models.Model):
    """Student's attempt to take a quiz"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Points earned")
    total_points = models.PositiveIntegerField(null=True, blank=True, help_text="Total points available")
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="Score %")
    is_passed = models.BooleanField(null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'quiz']
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.quiz.title}"


class UserAnswer(models.Model):
    """Individual answer to a question in a quiz attempt"""
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers')
    choice = models.ForeignKey(QuestionChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_answers')
    text_answer = models.TextField(blank=True, help_text="For short answer questions")
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['attempt', 'question']
        ordering = ['question__order']
    
    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.text[:30]}"


class Assignment(models.Model):
    """
    Домашнее задание в уроке
    Студент отправляет работу, преподаватель проверяет и выставляет оценку
    """
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='assignment')
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, help_text="Описание задания для студентов")
    max_points = models.PositiveIntegerField(default=100, help_text="Максимальное количество баллов")
    due_date = models.DateTimeField(null=True, blank=True, help_text="Дедлайн для сдачи")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"
    
    def __str__(self):
        return f"Assignment: {self.lesson.title}"


class AssignmentSubmission(models.Model):
    """
    Отправка домашнего задания студентом
    """
    STATUS_CHOICES = [
        ('submitted', 'Отправлено'),
        ('graded', 'Оценено'),
        ('returned', 'Возвращено на доработку'),
    ]
    
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    submitted_file = models.FileField(upload_to='assignments/submissions/', blank=True, null=True)
    submitted_text = models.TextField(blank=True, help_text="Текстовый ответ")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    
    # Оценка
    points_earned = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        help_text="Баллы за задание"
    )
    teacher_comment = models.TextField(blank=True, help_text="Комментарий преподавателя")
    graded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['assignment', 'student']
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.assignment.lesson.title}"
    
    @property
    def is_overdue(self):
        """Проверить, прошел ли дедлайн"""
        if not self.assignment.due_date:
            return False
        from django.utils import timezone
        return timezone.now() > self.assignment.due_date
    
    @property
    def is_late(self):
        """Проверить, была ли работа отправлена после дедлайна"""
        if not self.assignment.due_date:
            return False
        return self.submitted_at > self.assignment.due_date


class Certificate(models.Model):
    """
    Сертификат о завершении курса
    Выдается автоматически при достижении 100% прогресса
    """
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=50, unique=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    
    # Данные на момент выдачи (для неизменности сертификата)
    student_name = models.CharField(max_length=200)
    course_title = models.CharField(max_length=200)
    instructor_name = models.CharField(max_length=200)
    
    class Meta:
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"Certificate #{self.certificate_number} - {self.student_name}"
    
    def save(self, *args, **kwargs):
        if not self.certificate_number:
            import uuid
            self.certificate_number = f"CM-{uuid.uuid4().hex[:8].upper()}"
        if not self.student_name:
            user = self.enrollment.student
            self.student_name = user.get_full_name() or user.username
        if not self.course_title:
            self.course_title = self.enrollment.course.title
        if not self.instructor_name:
            instructor = self.enrollment.course.instructor
            self.instructor_name = instructor.get_full_name() or instructor.username
        super().save(*args, **kwargs)


class LessonComment(models.Model):
    """
    Комментарий к уроку (обсуждение)
    Поддерживает вложенные ответы (reply_to)
    """
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_comments')
    content = models.TextField(help_text="Текст комментария")
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_pinned = models.BooleanField(default=False, help_text="Закрепить комментарий")
    is_approved = models.BooleanField(default=True, help_text="Одобрен модератором")
    
    class Meta:
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."
    
    @property
    def is_edited(self):
        """Проверить, был ли комментарий отредактирован"""
        return self.updated_at > self.created_at

# ============================================================
# PAYMENT MODELS (Система платежей)
# ============================================================

class PaymentMethod(models.Model):
    """
    Способ оплаты
    """
    PAYMENT_TYPE_CHOICES = [
        ('stripe', 'Stripe Card'),
        ('paypal', 'PayPal'),
        ('yookassa', 'Yookassa (ЮKassa)'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    name = models.CharField(max_length=50, unique=True)
    type = models.CharField(max_length=50, choices=PAYMENT_TYPE_CHOICES)
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    logo_url = models.URLField(blank=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Purchase(models.Model):
    """
    Покупка курса студентом
    Связь между Student, Course и Payment
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидание платежа'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка платежа'),
        ('refunded', 'Возврат'),
        ('cancelled', 'Отменено'),
    ]
    
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='purchases')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Цена
    price = models.DecimalField(max_digits=8, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Промокод
    promo_code = models.CharField(max_length=50, blank=True)
    
    # Платеж
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True, unique=True)
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Возврат
    refund_reason = models.TextField(blank=True)
    refunded_at = models.DateTimeField(null=True, blank=True)
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student.username} - {self.course.title} ({self.status})"
    
    @property
    def is_completed(self):
        """Проверить, завершен ли платеж"""
        return self.status == 'completed'
    
    @property
    def discount_percentage(self):
        """Процент скидки от оригинальной цены"""
        if self.price == 0:
            return 0
        return round((self.discount_amount / self.price) * 100, 2)


class Payment(models.Model):
    """
    Запись о платеже в Stripe/PayPal/Yookassa
    """
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('succeeded', 'Успешно'),
        ('failed', 'Ошибка'),
        ('canceled', 'Отменено'),
    ]
    
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name='payment')
    
    # Данные платежа
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    currency = models.CharField(max_length=3, default='RUB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Stripe данные
    stripe_payment_intent_id = models.CharField(max_length=100, blank=True)
    stripe_client_secret = models.CharField(max_length=200, blank=True)
    
    # PayPal данные
    paypal_order_id = models.CharField(max_length=100, blank=True)
    
    # Yookassa данные
    yookassa_payment_id = models.CharField(max_length=100, blank=True)
    
    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Обработка ошибок
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payment #{self.id} - {self.purchase.student.username} ({self.status})"


class PromoCode(models.Model):
    """
    Промокод для скидки
    """
    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    
    # Скидка
    discount_type = models.CharField(
        max_length=10,
        choices=[('fixed', 'Fixed amount'), ('percent', 'Percentage')],
        default='percent'
    )
    discount_value = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Ограничения
    max_uses = models.IntegerField(null=True, blank=True, help_text="Максимум использований (пусто = неограниченно)")
    current_uses = models.IntegerField(default=0)
    
    # Действие
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    
    # Применимо к
    applicable_courses = models.ManyToManyField(Course, blank=True, related_name='promo_codes', help_text="Пусто = для всех курсов")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"PromoCode: {self.code} (-{self.discount_value}{('%' if self.discount_type == 'percent' else 'RUB')})"
    
    def is_valid(self):
        """Проверить, действителен ли промокод"""
        from django.utils import timezone
        now = timezone.now()
        
        if not self.is_active:
            return False
        
        if now < self.valid_from or now > self.valid_until:
            return False
        
        if self.max_uses and self.current_uses >= self.max_uses:
            return False
        
        return True
    
    def apply_discount(self, original_price):
        """Применить скидку к цене"""
        if self.discount_type == 'fixed':
            return max(0, original_price - self.discount_value)
        else:  # percent
            discount_amount = (original_price * self.discount_value) / 100
            return max(0, original_price - discount_amount)


class Refund(models.Model):
    """
    Возврат денежных средств
    """
    STATUS_CHOICES = [
        ('pending', 'В ожидании'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
        ('completed', 'Завершено'),
    ]
    
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='refunds')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refunds')
    
    reason = models.TextField(help_text="Причина возврата")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    refund_amount = models.DecimalField(max_digits=8, decimal_places=2)
    
    # Сроки
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Отказ
    rejection_reason = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Refund: {self.purchase.student.username} - {self.refund_amount} RUB ({self.status})"


# ============================================================
# MEDIA LIBRARY (Медиа-библиотека для преподавателей)
# ============================================================

class CourseMedia(models.Model):
    """
    Медиа-файл курса (изображения, видео, документы)
    Преподаватель загружает файлы в библиотеку, затем вставляет ссылки в уроки
    """
    MEDIA_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('document', 'Документ'),
        ('audio', 'Аудио'),
        ('other', 'Другое'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='media_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    
    # Файл
    file = models.FileField(upload_to='courses/media/%Y/%m/')
    original_filename = models.CharField(max_length=255, help_text="Оригинальное имя файла")
    
    # Метаданные
    title = models.CharField(max_length=200, blank=True, help_text="Название для отображения")
    description = models.TextField(blank=True, help_text="Описание файла")
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='other')
    
    # Размер и MIME-тип
    file_size = models.PositiveIntegerField(default=0, help_text="Размер файла в байтах")
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Для изображений: размеры
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Для видео/аудио: длительность
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Медиа-файл курса"
        verbose_name_plural = "Медиа-файлы курсов"
    
    def __str__(self):
        return f"{self.title or self.original_filename} ({self.course.title})"
    
    def save(self, *args, **kwargs):
        # Автоматически определить тип медиа по расширению
        if self.file and not self.media_type:
            ext = self.file.name.lower().split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp']:
                self.media_type = 'image'
            elif ext in ['mp4', 'webm', 'mov', 'avi', 'mkv']:
                self.media_type = 'video'
            elif ext in ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt']:
                self.media_type = 'document'
            elif ext in ['mp3', 'wav', 'ogg', 'flac', 'm4a']:
                self.media_type = 'audio'
            else:
                self.media_type = 'other'
        
        # Сохранить размер файла
        if self.file and hasattr(self.file, 'size'):
            self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    @property
    def file_size_display(self):
        """Человекочитаемый размер файла"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    @property
    def is_image(self):
        return self.media_type == 'image'
    
    @property
    def is_video(self):
        return self.media_type == 'video'
    
    @property
    def is_document(self):
        return self.media_type == 'document'
    
    @property
    def file_extension(self):
        """Расширение файла"""
        if self.original_filename:
            return self.original_filename.split('.')[-1].lower()
        return ''
    
    @property
    def markdown_embed(self):
        """Markdown код для вставки файла"""
        if self.is_image:
            return f"![{self.title or self.original_filename}]({self.file.url})"
        elif self.is_video:
            return f'<video src="{self.file.url}" controls width="100%"></video>'
        else:
            return f"[{self.title or self.original_filename}]({self.file.url})"
    
    @property
    def html_embed(self):
        """HTML код для вставки файла"""
        if self.is_image:
            return f'<img src="{self.file.url}" alt="{self.title or self.original_filename}" class="img-fluid">'
        elif self.is_video:
            return f'<video src="{self.file.url}" controls class="w-100"></video>'
        else:
            return f'<a href="{self.file.url}" target="_blank">{self.title or self.original_filename}</a>'