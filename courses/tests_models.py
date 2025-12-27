"""
CourseMaster - Тесты моделей
Базовые unit тесты для моделей приложения courses
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

from courses.models import (
    Category, Course, Section, Lesson, Enrollment, LessonProgress,
    Review, Quiz, Question, QuestionChoice, QuizAttempt, UserAnswer,
    Assignment, AssignmentSubmission, Certificate, LessonComment,
    PaymentMethod, Purchase, Payment, PromoCode
)


class CategoryModelTest(TestCase):
    """Тесты для модели Category"""
    
    def test_create_category(self):
        """Тест создания категории"""
        category = Category.objects.create(
            name='Programming',
            description='Programming courses',
            icon='💻'
        )
        self.assertEqual(category.name, 'Programming')
        self.assertEqual(category.slug, 'programming')  # Автогенерация slug
        self.assertEqual(str(category), 'Programming')
    
    def test_category_slug_auto_generation(self):
        """Тест автоматической генерации slug"""
        category = Category.objects.create(name='Web Development')
        self.assertEqual(category.slug, 'web-development')


class CourseModelTest(TestCase):
    """Тесты для модели Course"""
    
    def setUp(self):
        """Подготовка тестовых данных"""
        self.instructor = User.objects.create_user(
            username='instructor',
            email='instructor@test.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Python')
    
    def test_create_course(self):
        """Тест создания курса"""
        course = Course.objects.create(
            title='Django для начинающих',
            description='Основы Django',
            instructor=self.instructor,
            category=self.category,
            price=Decimal('1999.00'),
            level='beginner'
        )
        self.assertEqual(course.title, 'Django для начинающих')
        self.assertEqual(course.status, 'draft')  # Статус по умолчанию
        self.assertEqual(course.instructor, self.instructor)
        self.assertIsNotNone(course.slug)
    
    def test_course_slug_auto_generation(self):
        """Тест автоматической генерации slug курса"""
        course = Course.objects.create(
            title='Python Basics',
            instructor=self.instructor
        )
        self.assertEqual(course.slug, 'python-basics')
    
    def test_course_current_price_with_discount(self):
        """Тест получения текущей цены со скидкой"""
        course = Course.objects.create(
            title='Test Course',
            instructor=self.instructor,
            price=Decimal('1000.00'),
            discount_price=Decimal('799.00')
        )
        self.assertEqual(course.current_price, Decimal('799.00'))
        self.assertTrue(course.has_discount)
    
    def test_course_current_price_without_discount(self):
        """Тест получения текущей цены без скидки"""
        course = Course.objects.create(
            title='Test Course',
            instructor=self.instructor,
            price=Decimal('1000.00')
        )
        self.assertEqual(course.current_price, Decimal('1000.00'))
        self.assertFalse(course.has_discount)
    
    def test_course_free(self):
        """Тест бесплатного курса"""
        course = Course.objects.create(
            title='Free Course',
            instructor=self.instructor,
            is_free=True,
            price=Decimal('1000.00')
        )
        self.assertEqual(course.current_price, 0)


class SectionModelTest(TestCase):
    """Тесты для модели Section"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.course = Course.objects.create(title='Test Course', instructor=self.instructor)
    
    def test_create_section(self):
        """Тест создания раздела"""
        section = Section.objects.create(
            course=self.course,
            title='Введение',
            order=1
        )
        self.assertEqual(section.title, 'Введение')
        self.assertEqual(section.course, self.course)
        self.assertEqual(str(section), 'Test Course - Введение')


class LessonModelTest(TestCase):
    """Тесты для модели Lesson"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.course = Course.objects.create(title='Test Course', instructor=self.instructor)
        self.section = Section.objects.create(course=self.course, title='Section 1', order=1)
    
    def test_create_lesson(self):
        """Тест создания урока"""
        lesson = Lesson.objects.create(
            section=self.section,
            title='Урок 1: Введение',
            duration_minutes=30,
            order=1
        )
        self.assertEqual(lesson.title, 'Урок 1: Введение')
        self.assertEqual(lesson.duration_minutes, 30)
    
    def test_lesson_steps(self):
        """Тест добавления шагов к уроку"""
        from .models import Step
        lesson = Lesson.objects.create(
            section=self.section,
            title='Урок со шагами',
            order=1
        )
        step = Step.objects.create(
            lesson=lesson,
            step_type='text',
            title='Введение',
            order=0,
            content={'html': '<p>Hello</p>'}
        )
        self.assertEqual(lesson.steps.count(), 1)
        self.assertEqual(step.step_type, 'text')


class EnrollmentModelTest(TestCase):
    """Тесты для модели Enrollment"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.student = User.objects.create_user(username='student', password='pass')
        self.course = Course.objects.create(title='Test Course', instructor=self.instructor)
    
    def test_create_enrollment(self):
        """Тест записи на курс"""
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)
        self.assertFalse(enrollment.completed)
        self.assertEqual(enrollment.progress_percentage, 0)
    
    def test_enrollment_unique_constraint(self):
        """Тест уникальности записи (студент + курс)"""
        Enrollment.objects.create(student=self.student, course=self.course)
        
        # Попытка создать дублирующую запись должна вызвать ошибку
        with self.assertRaises(Exception):
            Enrollment.objects.create(student=self.student, course=self.course)


class ReviewModelTest(TestCase):
    """Тесты для модели Review"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.student = User.objects.create_user(username='student', password='pass')
        self.course = Course.objects.create(title='Test Course', instructor=self.instructor)
    
    def test_create_review(self):
        """Тест создания отзыва"""
        review = Review.objects.create(
            course=self.course,
            student=self.student,
            rating=5,
            title='Отличный курс!',
            comment='Очень понравилось, рекомендую!'
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.course, self.course)
        self.assertTrue(review.is_approved)  # По умолчанию одобрен


class QuizModelTest(TestCase):
    """Тесты для модели Quiz"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass')
        self.course = Course.objects.create(title='Test Course', instructor=self.instructor)
        self.section = Section.objects.create(course=self.course, title='Section 1', order=1)
        self.lesson = Lesson.objects.create(
            section=self.section, 
            title='Quiz Lesson', 
            order=1
        )
    
    def test_create_quiz(self):
        """Тест создания теста"""
        quiz = Quiz.objects.create(
            lesson=self.lesson,
            title='Тест по основам',
            pass_percentage=70,
            attempts_limit=3
        )
        self.assertEqual(quiz.pass_percentage, 70)
        self.assertEqual(quiz.attempts_limit, 3)


class CertificateModelTest(TestCase):
    """Тесты для модели Certificate"""
    
    def setUp(self):
        self.instructor = User.objects.create_user(
            username='instructor', 
            first_name='Иван',
            last_name='Петров',
            password='pass'
        )
        self.student = User.objects.create_user(
            username='student',
            first_name='Анна',
            last_name='Сидорова',
            password='pass'
        )
        self.course = Course.objects.create(title='Python Basics', instructor=self.instructor)
        self.enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            completed=True
        )
    
    def test_create_certificate(self):
        """Тест создания сертификата"""
        certificate = Certificate.objects.create(enrollment=self.enrollment)
        
        # Проверяем автоматическое заполнение полей
        self.assertIsNotNone(certificate.certificate_number)
        self.assertTrue(certificate.certificate_number.startswith('CM-'))
        self.assertEqual(certificate.student_name, 'Анна Сидорова')
        self.assertEqual(certificate.course_title, 'Python Basics')
        self.assertEqual(certificate.instructor_name, 'Иван Петров')


class PromoCodeModelTest(TestCase):
    """Тесты для модели PromoCode"""
    
    def test_promo_code_percent_discount(self):
        """Тест процентной скидки"""
        promo = PromoCode.objects.create(
            code='SALE20',
            discount_type='percent',
            discount_value=Decimal('20'),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=30)
        )
        
        original_price = Decimal('1000.00')
        final_price = promo.apply_discount(original_price)
        self.assertEqual(final_price, Decimal('800.00'))
    
    def test_promo_code_fixed_discount(self):
        """Тест фиксированной скидки"""
        promo = PromoCode.objects.create(
            code='MINUS100',
            discount_type='fixed',
            discount_value=Decimal('100'),
            valid_from=timezone.now(),
            valid_until=timezone.now() + timezone.timedelta(days=30)
        )
        
        original_price = Decimal('1000.00')
        final_price = promo.apply_discount(original_price)
        self.assertEqual(final_price, Decimal('900.00'))
    
    def test_promo_code_validity(self):
        """Тест валидности промокода"""
        # Активный промокод
        active_promo = PromoCode.objects.create(
            code='ACTIVE',
            discount_type='percent',
            discount_value=Decimal('10'),
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_until=timezone.now() + timezone.timedelta(days=30),
            is_active=True
        )
        self.assertTrue(active_promo.is_valid())
        
        # Просроченный промокод
        expired_promo = PromoCode.objects.create(
            code='EXPIRED',
            discount_type='percent',
            discount_value=Decimal('10'),
            valid_from=timezone.now() - timezone.timedelta(days=30),
            valid_until=timezone.now() - timezone.timedelta(days=1),
            is_active=True
        )
        self.assertFalse(expired_promo.is_valid())
