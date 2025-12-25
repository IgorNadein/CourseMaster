from django.test import TestCase
from django.contrib.auth.models import User
from .models import Category, Course, Section, Lesson, Enrollment, Review


class CategoryModelTests(TestCase):
    def test_category_creation(self):
        category = Category.objects.create(name="Programming")
        self.assertEqual(str(category), "Programming")
        self.assertEqual(category.slug, "programming")


class CourseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='instructor', password='pass123')
        self.category = Category.objects.create(name="Web Development")
        
    def test_course_creation(self):
        course = Course.objects.create(
            title="Django Masterclass",
            instructor=self.user,
            category=self.category,
            price=49.99
        )
        self.assertEqual(str(course), "Django Masterclass")
        self.assertEqual(course.slug, "django-masterclass")
        self.assertEqual(course.status, 'draft')
    
    def test_course_current_price(self):
        course = Course.objects.create(
            title="Test Course",
            instructor=self.user,
            price=99.99,
            discount_price=49.99
        )
        self.assertEqual(course.current_price, 49.99)
        self.assertTrue(course.has_discount)
    
    def test_free_course(self):
        course = Course.objects.create(
            title="Free Course",
            instructor=self.user,
            is_free=True,
            price=0
        )
        self.assertEqual(course.current_price, 0)


class SectionModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='instructor', password='pass123')
        self.course = Course.objects.create(
            title="Test Course",
            instructor=self.user
        )
    
    def test_section_creation(self):
        section = Section.objects.create(
            course=self.course,
            title="Introduction",
            order=1
        )
        self.assertEqual(str(section), "Test Course - Introduction")
        self.assertEqual(section.order, 1)


class LessonModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='instructor', password='pass123')
        self.course = Course.objects.create(title="Test Course", instructor=self.user)
        self.section = Section.objects.create(course=self.course, title="Section 1", order=1)
    
    def test_lesson_creation(self):
        lesson = Lesson.objects.create(
            section=self.section,
            title="Introduction Video",
            lesson_type='video',
            duration_minutes=10,
            order=1
        )
        self.assertEqual(str(lesson), "Section 1 - Introduction Video")
        self.assertEqual(lesson.lesson_type, 'video')


class EnrollmentModelTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass123')
        self.student = User.objects.create_user(username='student', password='pass123')
        self.course = Course.objects.create(title="Test Course", instructor=self.instructor)
    
    def test_enrollment_creation(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )
        self.assertEqual(str(enrollment), "student - Test Course")
        self.assertFalse(enrollment.completed)
        self.assertEqual(enrollment.progress_percentage, 0.0)


class ReviewModelTests(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(username='instructor', password='pass123')
        self.student = User.objects.create_user(username='student', password='pass123')
        self.course = Course.objects.create(title="Test Course", instructor=self.instructor)
    
    def test_review_creation(self):
        review = Review.objects.create(
            course=self.course,
            student=self.student,
            rating=5,
            title="Great course!",
            comment="Loved it!"
        )
        self.assertEqual(review.rating, 5)
        self.assertTrue(review.is_approved)

