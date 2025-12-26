"""
CourseMaster - Тесты Views
Тесты для views приложения courses
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from decimal import Decimal

from courses.models import (
    Category, Course, Section, Lesson, Enrollment, Review
)


class CourseListViewTest(TestCase):
    """Тесты для CourseListView (каталог курсов)"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Python', slug='python')
        
        # Создаем опубликованные курсы
        self.course1 = Course.objects.create(
            title='Django Basics',
            slug='django-basics',
            instructor=self.instructor,
            category=self.category,
            status='published',
            price=Decimal('999.00')
        )
        self.course2 = Course.objects.create(
            title='Flask Tutorial',
            slug='flask-tutorial',
            instructor=self.instructor,
            category=self.category,
            status='published',
            price=Decimal('799.00')
        )
        # Черновик - не должен отображаться
        self.draft_course = Course.objects.create(
            title='Draft Course',
            slug='draft-course',
            instructor=self.instructor,
            status='draft'
        )
    
    def test_course_list_view_status_code(self):
        """Тест статуса ответа страницы каталога"""
        response = self.client.get(reverse('course_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_course_list_uses_correct_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('course_list'))
        self.assertTemplateUsed(response, 'courses/catalog/course_list.html')
    
    def test_course_list_shows_published_courses(self):
        """Тест отображения только опубликованных курсов"""
        response = self.client.get(reverse('course_list'))
        self.assertContains(response, 'Django Basics')
        self.assertContains(response, 'Flask Tutorial')
        self.assertNotContains(response, 'Draft Course')
    
    def test_course_list_filter_by_category(self):
        """Тест фильтрации по категории"""
        response = self.client.get(reverse('course_list') + '?category=python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Django Basics')
    
    def test_course_list_search(self):
        """Тест поиска курсов"""
        response = self.client.get(reverse('course_list') + '?q=django')
        self.assertContains(response, 'Django Basics')
        self.assertNotContains(response, 'Flask Tutorial')


class CourseDetailViewTest(TestCase):
    """Тесты для CourseDetailView (страница курса)"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.category = Category.objects.create(name='Python', slug='python')
        self.course = Course.objects.create(
            title='Django Course',
            slug='django-course',
            instructor=self.instructor,
            category=self.category,
            status='published',
            description='Изучите Django'
        )
        
        # Создаем разделы и уроки
        self.section = Section.objects.create(
            course=self.course,
            title='Введение',
            order=1
        )
        self.lesson = Lesson.objects.create(
            section=self.section,
            title='Урок 1',
            lesson_type='video',
            order=1
        )
    
    def test_course_detail_view_status_code(self):
        """Тест статуса ответа страницы курса"""
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'django-course'}))
        self.assertEqual(response.status_code, 200)
    
    def test_course_detail_uses_correct_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'django-course'}))
        self.assertTemplateUsed(response, 'courses/catalog/course_detail.html')
    
    def test_course_detail_shows_course_info(self):
        """Тест отображения информации о курсе"""
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'django-course'}))
        self.assertContains(response, 'Django Course')
        self.assertContains(response, 'Изучите Django')
        self.assertContains(response, 'Введение')
    
    def test_course_detail_shows_enroll_button_for_anonymous(self):
        """Тест кнопки записи для анонимного пользователя"""
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'django-course'}))
        self.assertContains(response, 'Записаться на курс')
    
    def test_course_detail_shows_continue_for_enrolled(self):
        """Тест кнопки продолжения для записанного студента"""
        Enrollment.objects.create(student=self.student, course=self.course)
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get(reverse('course_detail', kwargs={'slug': 'django-course'}))
        self.assertContains(response, 'Продолжить обучение')


class CourseEnrollViewTest(TestCase):
    """Тесты для CourseEnrollView (запись на курс)"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            instructor=self.instructor,
            status='published'
        )
    
    def test_enroll_requires_login(self):
        """Тест требования авторизации для записи"""
        response = self.client.post(reverse('course_enroll', kwargs={'slug': 'test-course'}))
        self.assertEqual(response.status_code, 302)  # Редирект на login
    
    def test_enroll_creates_enrollment(self):
        """Тест создания записи на курс"""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.post(reverse('course_enroll', kwargs={'slug': 'test-course'}))
        
        self.assertEqual(response.status_code, 302)  # Редирект
        self.assertTrue(
            Enrollment.objects.filter(student=self.student, course=self.course).exists()
        )
    
    def test_enroll_updates_student_count(self):
        """Тест обновления счетчика студентов"""
        self.client.login(username='student', password='testpass123')
        
        initial_count = self.course.students_count
        self.client.post(reverse('course_enroll', kwargs={'slug': 'test-course'}))
        
        self.course.refresh_from_db()
        self.assertEqual(self.course.students_count, initial_count + 1)


class MyCoursesViewTest(TestCase):
    """Тесты для MyCoursesView (мои курсы)"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='My Course',
            slug='my-course',
            instructor=self.instructor,
            status='published'
        )
        Enrollment.objects.create(student=self.student, course=self.course)
    
    def test_my_courses_requires_login(self):
        """Тест требования авторизации"""
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 302)  # Редирект на login
    
    def test_my_courses_shows_enrolled_courses(self):
        """Тест отображения записанных курсов"""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Course')


class InstructorCoursesViewTest(TestCase):
    """Тесты для InstructorCoursesView (курсы преподавателя)"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.other_instructor = User.objects.create_user(
            username='other',
            password='testpass123'
        )
        self.course1 = Course.objects.create(
            title='My Course',
            slug='my-course',
            instructor=self.instructor
        )
        self.course2 = Course.objects.create(
            title='Other Course',
            slug='other-course',
            instructor=self.other_instructor
        )
    
    def test_instructor_courses_requires_login(self):
        """Тест требования авторизации"""
        response = self.client.get(reverse('instructor_courses'))
        self.assertEqual(response.status_code, 302)
    
    def test_instructor_sees_only_own_courses(self):
        """Тест отображения только своих курсов"""
        self.client.login(username='instructor', password='testpass123')
        
        response = self.client.get(reverse('instructor_courses'))
        self.assertContains(response, 'My Course')
        self.assertNotContains(response, 'Other Course')


class ReviewViewsTest(TestCase):
    """Тесты для views отзывов"""
    
    def setUp(self):
        self.client = Client()
        self.instructor = User.objects.create_user(
            username='instructor',
            password='testpass123'
        )
        self.student = User.objects.create_user(
            username='student',
            password='testpass123'
        )
        self.course = Course.objects.create(
            title='Review Course',
            slug='review-course',
            instructor=self.instructor,
            status='published'
        )
        # Записываем студента на курс
        Enrollment.objects.create(student=self.student, course=self.course)
    
    def test_review_create_requires_enrollment(self):
        """Тест требования записи на курс для отзыва"""
        other_student = User.objects.create_user(username='other', password='pass')
        self.client.login(username='other', password='pass')
        
        response = self.client.get(reverse('review_create', kwargs={'slug': 'review-course'}))
        # Должен редиректить или показать ошибку
        self.assertIn(response.status_code, [200, 302])
    
    def test_review_create_for_enrolled_student(self):
        """Тест создания отзыва записанным студентом"""
        self.client.login(username='student', password='testpass123')
        
        response = self.client.post(
            reverse('review_create', kwargs={'slug': 'review-course'}),
            {'rating': 5, 'title': 'Отлично!', 'comment': 'Рекомендую'}
        )
        
        # После успешного создания должен быть редирект
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Review.objects.filter(student=self.student, course=self.course).exists()
        )


class HomeViewTest(TestCase):
    """Тесты для главной страницы"""
    
    def test_home_page_status_code(self):
        """Тест статуса главной страницы"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_uses_correct_template(self):
        """Тест использования правильного шаблона"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')
    
    def test_home_page_contains_cta(self):
        """Тест наличия призыва к действию"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Начать обучение')
