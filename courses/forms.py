from django import forms
from .models import Course, Section, Lesson, Category


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
