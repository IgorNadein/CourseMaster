from django import forms
from .models import (Course, Section, Lesson, Category, Quiz, Question, QuestionChoice, Assignment, 
                     AssignmentSubmission, Review, LessonComment, Purchase, Payment, PromoCode)


class CourseForm(forms.ModelForm):
    """Форма создания/редактирования курса"""
    
    class Meta:
        model = Course
        fields = [
            'title', 'subtitle', 'description', 'category',
            'thumbnail', 'preview_video', 'level', 'language',
            'duration_hours', 'price', 'discount_price', 'is_free',
            'learning_outcomes', 'requirements', 'target_audience'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название курса'
            }),
            'subtitle': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Краткое описание курса'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Полное описание курса'
            }),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'preview_video': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'level': forms.Select(attrs={'class': 'form-select'}),
            'language': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Русский'
            }),
            'duration_hours': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.5',
                'min': '0'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'discount_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'learning_outcomes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Чему научатся студенты (по одному пункту на строку)'
            }),
            'requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Требования к студентам (по одному пункту на строку)'
            }),
            'target_audience': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Для кого этот курс (по одному пункту на строку)'
            }),
        }
        labels = {
            'title': 'Название курса',
            'subtitle': 'Подзаголовок',
            'description': 'Описание',
            'category': 'Категория',
            'thumbnail': 'Обложка курса',
            'preview_video': 'Превью видео (URL)',
            'level': 'Уровень сложности',
            'language': 'Язык',
            'duration_hours': 'Длительность (часы)',
            'price': 'Цена (₽)',
            'discount_price': 'Цена со скидкой (₽)',
            'is_free': 'Бесплатный курс',
            'learning_outcomes': 'Чему научатся студенты',
            'requirements': 'Требования',
            'target_audience': 'Целевая аудитория',
        }


class SectionForm(forms.ModelForm):
    """Форма создания/редактирования раздела курса"""
    
    class Meta:
        model = Section
        fields = ['title', 'description', 'order']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название раздела'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание раздела (опционально)'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'title': 'Название раздела',
            'description': 'Описание',
            'order': 'Порядок',
        }


class LessonForm(forms.ModelForm):
    """Форма создания/редактирования урока"""
    
    class Meta:
        model = Lesson
        fields = [
            'title', 'lesson_type', 'content', 'video_url',
            'duration_minutes', 'attachment', 'is_preview', 'order'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название урока'
            }),
            'lesson_type': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Содержание урока или заметки'
            }),
            'video_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://youtube.com/...'
            }),
            'duration_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'is_preview': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
        }
        labels = {
            'title': 'Название урока',
            'lesson_type': 'Тип урока',
            'content': 'Содержание',
            'video_url': 'Видео URL',
            'duration_minutes': 'Длительность (минуты)',
            'attachment': 'Материалы',
            'is_preview': 'Доступен для предпросмотра',
            'order': 'Порядок',
        }


class CoursePublishForm(forms.Form):
    """Форма публикации курса"""
    confirm = forms.BooleanField(
        required=True,
        label='Я подтверждаю, что курс готов к публикации',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class QuizForm(forms.ModelForm):
    """Форма создания/редактирования теста"""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'pass_percentage', 'time_limit_minutes', 
                  'attempts_limit', 'shuffle_questions', 'show_answers']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название теста'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание теста'
            }),
            'pass_percentage': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 100
            }),
            'time_limit_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Оставьте пусто для неограниченного времени'
            }),
            'attempts_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'shuffle_questions': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'show_answers': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class QuestionForm(forms.ModelForm):
    """Форма создания/редактирования вопроса"""
    
    class Meta:
        model = Question
        fields = ['text', 'type', 'points', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Текст вопроса'
            }),
            'type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'explanation': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Объяснение (показывается после ответа)'
            }),
        }


class QuestionChoiceForm(forms.ModelForm):
    """Форма для варианта ответа"""
    
    class Meta:
        model = QuestionChoice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Текст варианта ответа'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


class AssignmentForm(forms.ModelForm):
    """Форма создания/редактирования домашнего задания"""
    
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'max_points', 'due_date']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название задания'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Описание задания для студентов'
            }),
            'max_points': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '100'
            }),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }


class AssignmentSubmissionForm(forms.ModelForm):
    """Форма отправки домашнего задания студентом"""
    
    class Meta:
        model = AssignmentSubmission
        fields = ['submitted_text', 'submitted_file']
        widgets = {
            'submitted_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Введите ваш ответ здесь...'
            }),
            'submitted_file': forms.FileInput(attrs={
                'class': 'form-control'
            }),
        }


class AssignmentGradeForm(forms.ModelForm):
    """Форма проверки и оценки домашнего задания преподавателем"""
    
    class Meta:
        model = AssignmentSubmission
        fields = ['status', 'points_earned', 'teacher_comment']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'points_earned': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'teacher_comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ваш комментарий к работе студента...'
            }),
        }


class ReviewForm(forms.ModelForm):
    """Форма отзыва о курсе"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(attrs={'class': 'star-rating'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Заголовок отзыва (необязательно)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Поделитесь своим мнением о курсе...'
            }),
        }
        labels = {
            'rating': 'Оценка',
            'title': 'Заголовок',
            'comment': 'Отзыв',
        }


class LessonCommentForm(forms.ModelForm):
    """Форма комментария к уроку"""
    
    class Meta:
        model = LessonComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Напишите ваш вопрос или комментарий...'
            }),
        }
        labels = {
            'content': 'Комментарий',
        }

# ============================================================
# PAYMENT FORMS (Формы для платежей)
# ============================================================

class CheckoutForm(forms.Form):
    """Форма оформления покупки курса"""
    
    PAYMENT_METHOD_CHOICES = [
        ('stripe', 'Stripe Card'),
        ('paypal', 'PayPal'),
        ('yookassa', 'Yookassa (Яндекс.Касса)'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Способ оплаты'
    )
    
    promo_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите промокод (опционально)',
            'maxlength': '50'
        }),
        label='Промокод'
    )
    
    agree_terms = forms.BooleanField(
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Я согласен с условиями использования',
        required=True
    )


class StripePaymentForm(forms.Form):
    """Форма для Stripe платежа"""
    
    cardholder_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя владельца карты'
        }),
        label='Имя'
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        }),
        label='Email'
    )
    
    # stripe_token будет добавлена через JavaScript


class PayPalReturnForm(forms.Form):
    """Форма для обработки возврата из PayPal"""
    pass


class RefundRequestForm(forms.Form):
    """Форма запроса возврата денежных средств"""
    
    REFUND_REASONS = [
        ('not_satisfied', 'Не удовлетворен качеством'),
        ('changed_mind', 'Передумал изучать курс'),
        ('technical_issues', 'Технические проблемы'),
        ('duplicate_purchase', 'Случайная двойная покупка'),
        ('other', 'Другая причина'),
    ]
    
    reason = forms.ChoiceField(
        choices=REFUND_REASONS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Причина возврата'
    )
    
    details = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Дополнительные подробности (опционально)'
        }),
        label='Дополнительная информация'
    )


class PromoCodeForm(forms.Form):
    """Форма проверки промокода"""
    
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите промокод'
        }),
        label='Промокод'
    )