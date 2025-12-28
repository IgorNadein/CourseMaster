from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from decimal import Decimal
from .models import (Course, Category, Enrollment, Section, Lesson, LessonProgress, Review, 
                     Quiz, Question, QuestionChoice, QuizAttempt, UserAnswer, Assignment, AssignmentSubmission,
                     Certificate, LessonComment, Payment, Purchase, PromoCode, Refund, PaymentMethod, CourseMedia,
                     Step, StepProgress)
from .forms import (CourseForm, SectionForm, LessonForm, CoursePublishForm, QuizForm, QuestionForm, 
                    QuestionChoiceForm, QuestionChoiceFormSet, AssignmentForm, AssignmentSubmissionForm, AssignmentGradeForm, ReviewForm,
                    LessonCommentForm, CheckoutForm, StripePaymentForm, RefundRequestForm, PromoCodeForm,
                    CourseMediaUploadForm, CourseMediaEditForm)

# Импорт AJAX views для quiz builder
from .ajax_views import (
    QuizBuilderView, QuizUpdateAjaxView, QuestionCreateAjaxView, QuestionUpdateAjaxView,
    QuestionDeleteAjaxView, QuestionDuplicateAjaxView, ChoiceCreateAjaxView, 
    ChoiceUpdateAjaxView, ChoiceDeleteAjaxView
)

# Импорт AJAX views для course builder
from .ajax_views import (
    CourseBuilderView, CourseUpdateAjaxView, CoursePublishAjaxView, CourseUnpublishAjaxView,
    SectionCreateAjaxView, SectionUpdateAjaxView, SectionDeleteAjaxView,
    LessonCreateAjaxView, LessonGetAjaxView, LessonUpdateAjaxView, LessonDeleteAjaxView,
    QuizCreateAjaxView, AssignmentCreateAjaxView, AssignmentGetAjaxView, AssignmentUpdateAjaxView
)

# Импорт AJAX views для Step (шаги уроков)
from .ajax_views import (
    StepListAjaxView, StepCreateAjaxView, StepGetAjaxView, StepUpdateAjaxView,
    StepDeleteAjaxView, StepReorderAjaxView, StepDuplicateAjaxView,
    StepCheckAnswerView, StepCompleteView
)


class CourseListView(ListView):
    """
    Каталог курсов для студентов с фильтрацией и поиском
    """
    model = Course
    template_name = 'courses/catalog/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').exclude(slug='').select_related(
            'instructor', 'category'
        ).annotate(
            enrollments_count=Count('enrollments')
        )
        
        # Поиск
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(subtitle__icontains=search_query)
            )
        
        # Фильтр по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Фильтр по уровню
        level = self.request.GET.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        # Фильтр по цене
        price_filter = self.request.GET.get('price')
        if price_filter == 'free':
            queryset = queryset.filter(is_free=True)
        elif price_filter == 'paid':
            queryset = queryset.filter(is_free=False)
        
        # Сортировка
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['-created_at', 'price', '-price', '-average_rating', '-students_count']
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['current_category'] = self.request.GET.get('category', '')
        context['current_level'] = self.request.GET.get('level', '')
        context['current_price'] = self.request.GET.get('price', '')
        context['search_query'] = self.request.GET.get('q', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        
        # Статистика для студента
        if self.request.user.is_authenticated:
            context['my_enrollments'] = Enrollment.objects.filter(
                student=self.request.user
            ).values_list('course_id', flat=True)
        
        return context


class CourseDetailView(DetailView):
    """
    Детальная страница курса с программой и отзывами
    """
    model = Course
    template_name = 'courses/catalog/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Course.objects.select_related(
            'instructor', 'category'
        ).prefetch_related(
            'sections__lessons',
            'reviews__student'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Разделы и уроки
        context['sections'] = course.sections.prefetch_related('lessons').all()
        
        # Общая статистика курса
        context['total_lessons'] = Lesson.objects.filter(section__course=course).count()
        context['total_duration'] = sum(
            lesson.duration_minutes 
            for section in context['sections'] 
            for lesson in section.lessons.all()
        )
        
        # Отзывы
        context['reviews'] = course.reviews.filter(is_approved=True).select_related('student')[:10]
        context['reviews_count'] = course.reviews.filter(is_approved=True).count()
        
        # Статистика рейтинга
        rating_stats = course.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        context['avg_rating'] = rating_stats['avg_rating'] or 0
        context['total_reviews'] = rating_stats['total_reviews']
        
        # Проверка записи пользователя
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).exists()
            
            # Прогресс (если записан)
            if context['is_enrolled']:
                enrollment = Enrollment.objects.get(
                    student=self.request.user,
                    course=course
                )
                context['enrollment'] = enrollment
                context['progress_percentage'] = enrollment.progress_percentage
            
            # Проверка: есть ли отзыв от пользователя
            context['user_review'] = Review.objects.filter(
                student=self.request.user,
                course=course
            ).first()
        else:
            context['is_enrolled'] = False
        
        # Проверка - является ли пользователь преподавателем этого курса
        context['is_instructor'] = (
            self.request.user.is_authenticated and 
            course.instructor == self.request.user
        )
        
        return context


class CourseEnrollView(LoginRequiredMixin, View):
    """
    Запись студента на курс
    """
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, status='published')
        
        # Проверка - не записан ли уже
        enrollment, created = Enrollment.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        if created:
            # Увеличиваем счетчик студентов
            course.students_count += 1
            course.save(update_fields=['students_count'])
            
            messages.success(
                request, 
                f'Вы успешно записались на курс "{course.title}"!'
            )
        else:
            messages.info(
                request, 
                f'Вы уже записаны на курс "{course.title}".'
            )
        
        return redirect('course_detail', slug=course.slug)


class MyCoursesView(LoginRequiredMixin, ListView):
    """
    Личный кабинет студента - курсы в процессе обучения
    """
    model = Enrollment
    template_name = 'courses/learning/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 10
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related(
            'course__instructor', 'course__category'
        ).prefetch_related(
            'course__sections__lessons',
            'lesson_progress'
        ).order_by('-enrolled_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Статистика студента
        enrollments = self.get_queryset()
        context['total_courses'] = enrollments.count()
        context['completed_courses'] = enrollments.filter(completed=True).count()
        context['in_progress_courses'] = enrollments.filter(completed=False).count()
        
        # Средний прогресс
        if context['total_courses'] > 0:
            total_progress = sum(e.progress_percentage for e in enrollments)
            context['avg_progress'] = total_progress / context['total_courses']
        else:
            context['avg_progress'] = 0
        
        # Для каждого enrollment найти следующий непройденный урок
        enrollments_with_next_lesson = []
        for enrollment in context['enrollments']:
            # Получить все уроки курса в правильном порядке
            all_lessons = Lesson.objects.filter(
                section__course=enrollment.course
            ).order_by('section__order', 'order')
            
            # Получить ID пройденных уроков
            completed_lesson_ids = set(
                enrollment.lesson_progress.filter(completed=True).values_list('lesson_id', flat=True)
            )
            
            # Найти первый непройденный урок
            next_lesson = None
            for lesson in all_lessons:
                if lesson.id not in completed_lesson_ids:
                    next_lesson = lesson
                    break
            
            # Если все уроки пройдены, показать первый урок
            if next_lesson is None and all_lessons.exists():
                next_lesson = all_lessons.first()
            
            enrollments_with_next_lesson.append({
                'enrollment': enrollment,
                'next_lesson': next_lesson,
            })
        
        context['enrollments_data'] = enrollments_with_next_lesson
        
        return context


class LessonView(LoginRequiredMixin, DetailView):
    """
    Просмотр урока (только для записанных студентов)
    Урок содержит шаги (Step) - контент отображается пошагово
    """
    model = Lesson
    template_name = 'courses/learning/lesson_view.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'
    
    def get_queryset(self):
        return Lesson.objects.select_related(
            'section__course__instructor'
        ).prefetch_related(
            'section__lessons',
            'steps'  # Prefetch steps for Step-based lessons
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        course = lesson.section.course
        
        # Данные курса и раздела (добавляем сразу для доступа в шаблоне)
        context['course'] = course
        context['section'] = lesson.section
        
        # Проверка доступа
        if not lesson.is_preview:
            # Только для записанных студентов или преподавателя
            is_enrolled = Enrollment.objects.filter(
                student=self.request.user,
                course=course
            ).exists()
            is_instructor = course.instructor == self.request.user
            
            if not (is_enrolled or is_instructor):
                messages.error(
                    self.request,
                    'Запишитесь на курс для просмотра этого урока.'
                )
                return context
        
        # Все разделы и уроки для навигации
        context['sections'] = course.sections.prefetch_related('lessons').all()
        
        # Предыдущий и следующий урок
        all_lessons = Lesson.objects.filter(
            section__course=course
        ).order_by('section__order', 'order')
        
        lesson_list = list(all_lessons)
        current_index = lesson_list.index(lesson)
        
        context['previous_lesson'] = lesson_list[current_index - 1] if current_index > 0 else None
        context['next_lesson'] = lesson_list[current_index + 1] if current_index < len(lesson_list) - 1 else None
        
        # Прогресс урока
        enrollment = None
        if Enrollment.objects.filter(student=self.request.user, course=course).exists():
            enrollment = Enrollment.objects.get(student=self.request.user, course=course)
            lesson_progress, _ = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            context['lesson_progress'] = lesson_progress
            context['is_completed'] = lesson_progress.completed
            context['enrollment'] = enrollment
        
        # ============================================================
        # STEP-BASED CONTENT (Шаги урока)
        # ============================================================
        steps = lesson.steps.all().order_by('order')
        context['steps'] = steps
        context['has_steps'] = steps.exists()
        context['steps_count'] = steps.count()
        
        # Получить текущий шаг (из GET параметра или первый)
        current_step_id = self.request.GET.get('step')
        current_step = None
        current_step_index = 0
        
        if steps.exists():
            if current_step_id:
                try:
                    current_step = steps.get(id=current_step_id)
                    current_step_index = list(steps).index(current_step)
                except Step.DoesNotExist:
                    current_step = steps.first()
                    current_step_index = 0
            else:
                current_step = steps.first()
                current_step_index = 0
        
        context['current_step'] = current_step
        context['current_step_index'] = current_step_index
        
        # Предыдущий и следующий шаг
        step_list = list(steps)
        if current_step:
            context['previous_step'] = step_list[current_step_index - 1] if current_step_index > 0 else None
            context['next_step'] = step_list[current_step_index + 1] if current_step_index < len(step_list) - 1 else None
        
        # Прогресс по шагам
        if enrollment and steps.exists():
            step_progress_dict = {}
            completed_steps = 0
            
            for step in steps:
                progress, _ = StepProgress.objects.get_or_create(
                    enrollment=enrollment,
                    step=step,
                    defaults={'status': 'not_started'}
                )
                step_progress_dict[step.id] = progress
                if progress.completed:
                    completed_steps += 1
            
            context['step_progress'] = step_progress_dict
            context['completed_steps'] = completed_steps
            
            # Прогресс в процентах
            if steps.count() > 0:
                context['steps_progress_percent'] = round((completed_steps / steps.count()) * 100)
            else:
                context['steps_progress_percent'] = 0
            
            # Прогресс текущего шага
            if current_step:
                context['current_step_progress'] = step_progress_dict.get(current_step.id)
        
        # Комментарии к уроку
        context['comments'] = lesson.comments.filter(
            is_approved=True,
            reply_to__isnull=True  # Только родительские комментарии
        ).select_related('author').prefetch_related('replies__author')
        context['comments_count'] = lesson.comments.filter(is_approved=True).count()
        context['comment_form'] = LessonCommentForm()
        
        # Проверка: можно ли оставлять комментарии
        is_enrolled = Enrollment.objects.filter(student=self.request.user, course=course).exists()
        is_instructor = course.instructor == self.request.user
        context['can_comment'] = is_enrolled or is_instructor
        
        return context


class LessonCompleteView(LoginRequiredMixin, View):
    """
    Отметка урока как пройденного
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.section.course
        
        # Проверка записи на курс
        try:
            enrollment = Enrollment.objects.get(
                student=request.user,
                course=course
            )
        except Enrollment.DoesNotExist:
            messages.error(request, 'Вы не записаны на этот курс.')
            return redirect('course_detail', slug=course.slug)
        
        # Отметить урок как пройденный
        lesson_progress, created = LessonProgress.objects.get_or_create(
            enrollment=enrollment,
            lesson=lesson
        )
        
        if not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.completed_at = timezone.now()
            lesson_progress.save()
            
            # Обновить прогресс курса
            total_lessons = Lesson.objects.filter(section__course=course).count()
            completed_lessons = LessonProgress.objects.filter(
                enrollment=enrollment,
                completed=True
            ).count()
            
            enrollment.progress_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
            
            # Проверка завершения курса
            if enrollment.progress_percentage >= 100:
                enrollment.completed = True
                enrollment.completed_at = timezone.now()
                
                # Автоматически выдать сертификат
                if not hasattr(enrollment, 'certificate'):
                    Certificate.objects.create(enrollment=enrollment)
                    messages.success(
                        request,
                        f'🎉 Поздравляем! Вы завершили курс "{course.title}" и получили сертификат!'
                    )
                else:
                    messages.success(
                        request,
                        f'🎉 Поздравляем! Вы завершили курс "{course.title}"!'
                    )
            
            enrollment.save()
            
            messages.success(request, f'Урок "{lesson.title}" отмечен как пройденный.')
        
        # Перенаправить на следующий урок или на страницу курса
        next_lesson_id = request.POST.get('next_lesson_id')
        if next_lesson_id:
            return redirect('lesson_view', lesson_id=next_lesson_id)
        else:
            return redirect('course_detail', slug=course.slug)


# ============================================================
# ПРЕПОДАВАТЕЛЬСКИЕ VIEWS (Управление курсами)
# ============================================================

class InstructorCoursesView(LoginRequiredMixin, ListView):
    """
    Список курсов преподавателя
    """
    model = Course
    template_name = 'courses/instructor/course_list.html'
    context_object_name = 'courses'
    paginate_by = 10
    
    def get_queryset(self):
        return Course.objects.filter(
            instructor=self.request.user
        ).annotate(
            enrollments_count=Count('enrollments')
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        courses = self.get_queryset()
        
        # Статистика преподавателя
        context['total_courses'] = courses.count()
        context['published_courses'] = courses.filter(status='published').count()
        context['draft_courses'] = courses.filter(status='draft').count()
        context['total_students'] = sum(c.students_count for c in courses)
        
        return context


class CourseCreateView(LoginRequiredMixin, CreateView):
    """
    Создание нового курса
    """
    model = Course
    form_class = CourseForm
    template_name = 'courses/instructor/course_form.html'
    
    def form_valid(self, form):
        form.instance.instructor = self.request.user
        form.instance.status = 'draft'
        # Сохранить объект, чтобы slug был сгенерирован
        self.object = form.save()
        messages.success(
            self.request,
            'Курс успешно создан! Добавьте разделы и уроки в конструкторе.'
        )
        # Перенаправляем сразу в конструктор курса
        return redirect('course_builder', slug=self.object.slug)
    
    def get_success_url(self):
        return reverse('course_builder', kwargs={'slug': self.object.slug})


class CourseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование курса
    """
    model = Course
    form_class = CourseForm
    template_name = 'courses/instructor/course_form.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Курс успешно обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('course_builder', kwargs={'slug': self.object.slug})


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление курса
    """
    model = Course
    template_name = 'courses/instructor/course_confirm_delete.html'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    success_url = reverse_lazy('instructor_courses')
    
    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Курс успешно удален.')
        return super().delete(request, *args, **kwargs)


class InstructorCourseDetailView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Перенаправляет на конструктор курса (course_builder)
    Оставлен для обратной совместимости старых ссылок
    """
    def test_func(self):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug)
        return course.instructor == self.request.user
    
    def get(self, request, slug):
        return redirect('course_builder', slug=slug)


# SectionCreateView, SectionUpdateView, SectionDeleteView - УДАЛЕНЫ
# Теперь используется CourseBuilderView с AJAX API


# LessonCreateView, LessonUpdateView, LessonDeleteView - УДАЛЕНЫ
# Теперь используется CourseBuilderView с AJAX API


class CoursePublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Публикация курса (изменение статуса draft -> published)
    """
    def test_func(self):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug)
        return course.instructor == self.request.user
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        
        # Проверки перед публикацией
        if not course.sections.exists():
            messages.error(
                request,
                'Невозможно опубликовать курс без разделов. Добавьте хотя бы один раздел.'
            )
            return redirect('instructor_course_detail', slug=slug)
        
        total_lessons = Lesson.objects.filter(section__course=course).count()
        if total_lessons == 0:
            messages.error(
                request,
                'Невозможно опубликовать курс без уроков. Добавьте хотя бы один урок.'
            )
            return redirect('instructor_course_detail', slug=slug)
        
        # Публикация
        course.status = 'published'
        course.published_at = timezone.now()
        course.save()
        
        messages.success(
            request,
            f'🎉 Курс "{course.title}" успешно опубликован и доступен студентам!'
        )
        return redirect('instructor_course_detail', slug=slug)


class CourseUnpublishView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Снятие курса с публикации
    """
    def test_func(self):
        slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=slug)
        return course.instructor == self.request.user
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        course.status = 'draft'
        course.save()
        
        messages.success(
            request,
            f'Курс "{course.title}" снят с публикации.'
        )
        return redirect('instructor_course_detail', slug=slug)


# ============================================================
# QUIZ/TEST VIEWS (Система тестирования)
# ============================================================

class QuizTakeView(LoginRequiredMixin, View):
    """
    Студент проходит тест
    """
    template_name = 'courses/learning/quiz_take.html'
    
    def get(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        lesson = quiz.lesson
        course = lesson.section.course
        
        # Проверка: студент записан на курс?
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
        except Enrollment.DoesNotExist:
            messages.error(request, 'Вы не записаны на этот курс.')
            return redirect('course_detail', slug=course.slug)
        
        # Проверка: доступны ли попытки?
        attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz)
        if attempts.count() >= quiz.attempts_limit:
            messages.error(request, f'Вы исчерпали количество попыток ({quiz.attempts_limit}).')
            return redirect('lesson_view', lesson_id=lesson.id)
        
        # Создать новую попытку
        attempt = QuizAttempt.objects.create(student=request.user, quiz=quiz)
        
        # Получить вопросы
        questions = quiz.questions.all()
        if quiz.shuffle_questions:
            import random
            questions = list(questions)
            random.shuffle(questions)
        
        context = {
            'quiz': quiz,
            'lesson': lesson,
            'course': course,
            'attempt': attempt,
            'questions': questions,
            'total_questions': questions.count(),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        attempt = QuizAttempt.objects.get(id=request.POST.get('attempt_id'))
        
        # Проверка безопасности
        if attempt.student != request.user or attempt.quiz != quiz:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Обработать ответы
        total_points = 0
        earned_points = 0
        
        for question in quiz.questions.all():
            if question.type == 'text':
                # Текстовый ответ (ручная проверка)
                text_answer = request.POST.get(f'question_{question.id}', '')
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    text_answer=text_answer,
                    is_correct=None,  # Будет проверен преподавателем
                    points_earned=None
                )
            else:
                # Выбор ответа (автоматическая проверка)
                choice_id = request.POST.get(f'question_{question.id}')
                
                if choice_id:
                    choice = get_object_or_404(QuestionChoice, id=choice_id)
                    is_correct = choice.is_correct
                    points = question.points if is_correct else 0
                else:
                    choice = None
                    is_correct = False
                    points = 0
                
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    choice=choice,
                    is_correct=is_correct,
                    points_earned=points
                )
                earned_points += points
            
            total_points += question.points
        
        # Рассчитать результат
        percentage = (earned_points / total_points * 100) if total_points > 0 else 0
        is_passed = percentage >= quiz.pass_percentage
        
        attempt.completed_at = timezone.now()
        attempt.score = earned_points
        attempt.total_points = total_points
        attempt.percentage = percentage
        attempt.is_passed = is_passed
        attempt.save()
        
        return redirect('quiz_results', attempt_id=attempt.id)


class QuizResultsView(LoginRequiredMixin, DetailView):
    """
    Результаты теста студента
    """
    model = QuizAttempt
    template_name = 'courses/learning/quiz_results.html'
    context_object_name = 'attempt'
    pk_url_kwarg = 'attempt_id'
    
    def get_queryset(self):
        return QuizAttempt.objects.filter(student=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        attempt = self.object
        
        context['quiz'] = attempt.quiz
        context['lesson'] = attempt.quiz.lesson
        context['course'] = attempt.quiz.lesson.section.course
        context['answers'] = attempt.answers.select_related('question', 'choice').all()
        context['show_answers'] = attempt.quiz.show_answers
        
        return context


class InstructorQuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Преподаватель создает тест для урока
    """
    model = Quiz
    form_class = QuizForm
    template_name = 'courses/instructor/quiz_form.html'
    
    def test_func(self):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        return lesson.section.course.instructor == self.request.user
    
    def form_valid(self, form):
        lesson_id = self.kwargs.get('lesson_id')
        form.instance.lesson = get_object_or_404(Lesson, id=lesson_id)
        messages.success(self.request, 'Тест успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_quiz_detail', kwargs={'quiz_id': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        context['lesson'] = lesson
        context['course'] = lesson.section.course
        return context


class InstructorQuizDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Управление тестом преподавателем
    """
    model = Quiz
    template_name = 'courses/instructor/quiz_detail.html'
    context_object_name = 'quiz'
    pk_url_kwarg = 'quiz_id'
    
    def test_func(self):
        quiz = self.get_object()
        return quiz.lesson.section.course.instructor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz = self.object
        
        context['lesson'] = quiz.lesson
        context['course'] = quiz.lesson.section.course
        context['questions'] = quiz.questions.prefetch_related('choices').all()
        context['total_questions'] = quiz.questions.count()
        context['attempts'] = quiz.attempts.select_related('student').order_by('-started_at')[:10]
        
        return context


# QuestionCreateView, QuestionDetailView, QuestionUpdateView, QuestionDeleteView - УДАЛЕНЫ
# QuestionChoiceCreateView, QuestionChoiceUpdateView, QuestionChoiceDeleteView - УДАЛЕНЫ  
# Теперь используется QuizBuilderView с AJAX API


# ============================================================
# ASSIGNMENT/HOMEWORK VIEWS (Система домашних заданий)
# ============================================================

class AssignmentSubmitView(LoginRequiredMixin, CreateView):
    """
    Студент отправляет домашнее задание
    """
    model = AssignmentSubmission
    form_class = AssignmentSubmissionForm
    template_name = 'courses/assignments/assignment_submit.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment_id = self.kwargs.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id)
        lesson = assignment.lesson
        course = lesson.section.course
        
        context['assignment'] = assignment
        context['lesson'] = lesson
        context['course'] = course
        
        # Проверка: студент записан на курс?
        try:
            enrollment = Enrollment.objects.get(student=self.request.user, course=course)
            context['is_enrolled'] = True
        except Enrollment.DoesNotExist:
            context['is_enrolled'] = False
        
        # Попыталась ли студент уже отправить задание?
        try:
            submission = AssignmentSubmission.objects.get(
                assignment=assignment,
                student=self.request.user
            )
            context['existing_submission'] = submission
        except AssignmentSubmission.DoesNotExist:
            context['existing_submission'] = None
        
        return context
    
    def form_valid(self, form):
        assignment_id = self.kwargs.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        # Проверка: студент записан на курс?
        try:
            enrollment = Enrollment.objects.get(
                student=self.request.user,
                course=assignment.lesson.section.course
            )
        except Enrollment.DoesNotExist:
            messages.error(self.request, 'Вы не записаны на этот курс.')
            return self.form_invalid(form)
        
        # Проверка: уже ли отправлено?
        try:
            existing = AssignmentSubmission.objects.get(
                assignment=assignment,
                student=self.request.user
            )
            # Обновить существующую отправку
            form.instance = existing
        except AssignmentSubmission.DoesNotExist:
            pass
        
        form.instance.assignment = assignment
        form.instance.student = self.request.user
        form.instance.status = 'submitted'
        messages.success(self.request, 'Задание успешно отправлено!')
        return super().form_valid(form)
    
    def get_success_url(self):
        assignment_id = self.kwargs.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id)
        return reverse('lesson_view', kwargs={'lesson_id': assignment.lesson.id})


class InstructorAssignmentGradeView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Преподаватель проверяет и оценивает домашнее задание
    """
    model = AssignmentSubmission
    template_name = 'courses/instructor/assignment_grade.html'
    context_object_name = 'submission'
    pk_url_kwarg = 'submission_id'
    
    def test_func(self):
        submission = self.get_object()
        return submission.assignment.lesson.section.course.instructor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submission = self.object
        assignment = submission.assignment
        
        context['assignment'] = assignment
        context['lesson'] = assignment.lesson
        context['course'] = assignment.lesson.section.course
        context['form'] = AssignmentGradeForm(instance=submission)
        
        return context
    
    def post(self, request, *args, **kwargs):
        submission = self.get_object()
        form = AssignmentGradeForm(request.POST, instance=submission)
        
        if form.is_valid():
            form.instance.status = form.cleaned_data['status']
            form.instance.points_earned = form.cleaned_data['points_earned']
            form.instance.teacher_comment = form.cleaned_data['teacher_comment']
            form.instance.graded_at = timezone.now()
            form.save()
            
            messages.success(request, f'Задание студента "{submission.student.get_full_name}" оценено!')
            return redirect('instructor_assignment_detail', assignment_id=submission.assignment.id)
        
        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)


class InstructorAssignmentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Просмотр всех отправок домашнего задания преподавателем
    """
    model = Assignment
    template_name = 'courses/instructor/assignment_detail.html'
    context_object_name = 'assignment'
    pk_url_kwarg = 'assignment_id'
    
    def test_func(self):
        assignment = self.get_object()
        return assignment.lesson.section.course.instructor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignment = self.object
        
        context['lesson'] = assignment.lesson
        context['course'] = assignment.lesson.section.course
        context['submissions'] = assignment.submissions.select_related('student').order_by('-submitted_at')
        context['total_submissions'] = assignment.submissions.count()
        context['graded_submissions'] = assignment.submissions.filter(status='graded').count()
        
        # Статистика оценок
        graded = assignment.submissions.filter(status='graded', points_earned__isnull=False)
        if graded.exists():
            from django.db.models import Avg
            avg_score = graded.aggregate(Avg('points_earned'))['points_earned__avg']
            context['avg_score'] = round(avg_score, 2) if avg_score else 0
        else:
            context['avg_score'] = 0
        
        return context


class InstructorAssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Преподаватель создает домашнее задание для урока
    """
    model = Assignment
    form_class = AssignmentForm
    template_name = 'courses/instructor/assignment_form.html'
    
    def test_func(self):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        return lesson.section.course.instructor == self.request.user
    
    def form_valid(self, form):
        lesson_id = self.kwargs.get('lesson_id')
        form.instance.lesson = get_object_or_404(Lesson, id=lesson_id)
        messages.success(self.request, 'Задание успешно создано!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_assignment_detail', kwargs={'assignment_id': self.object.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        context['lesson'] = lesson
        context['course'] = lesson.section.course
        return context


# ============================================================
# REVIEW VIEWS (Система отзывов и рейтингов)
# ============================================================

class ReviewCreateView(LoginRequiredMixin, CreateView):
    """
    Студент оставляет отзыв о курсе
    """
    model = Review
    form_class = ReviewForm
    template_name = 'courses/reviews/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, slug=kwargs.get('slug'))
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        
        # Проверка: записан ли студент на курс
        context['is_enrolled'] = Enrollment.objects.filter(
            student=self.request.user,
            course=self.course
        ).exists()
        
        # Проверка: уже есть отзыв?
        context['existing_review'] = Review.objects.filter(
            student=self.request.user,
            course=self.course
        ).first()
        
        return context
    
    def form_valid(self, form):
        # Проверка: записан ли студент на курс
        if not Enrollment.objects.filter(student=self.request.user, course=self.course).exists():
            messages.error(self.request, 'Вы должны быть записаны на курс, чтобы оставить отзыв.')
            return redirect('course_detail', slug=self.course.slug)
        
        # Проверка: уже есть отзыв?
        existing = Review.objects.filter(student=self.request.user, course=self.course).first()
        if existing:
            messages.info(self.request, 'Вы уже оставили отзыв. Вы можете его отредактировать.')
            return redirect('review_update', slug=self.course.slug)
        
        form.instance.course = self.course
        form.instance.student = self.request.user
        
        response = super().form_valid(form)
        
        # Обновить средний рейтинг курса
        self._update_course_rating()
        
        messages.success(self.request, 'Спасибо за ваш отзыв!')
        return response
    
    def _update_course_rating(self):
        """Обновить средний рейтинг и количество отзывов курса"""
        stats = Review.objects.filter(
            course=self.course,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        self.course.average_rating = stats['avg_rating'] or 0
        self.course.total_reviews = stats['total_reviews']
        self.course.save(update_fields=['average_rating', 'total_reviews'])
    
    def get_success_url(self):
        return reverse('course_detail', kwargs={'slug': self.course.slug})


class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """
    Студент редактирует свой отзыв
    """
    model = Review
    form_class = ReviewForm
    template_name = 'courses/reviews/review_form.html'
    
    def get_object(self, queryset=None):
        course = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        return get_object_or_404(Review, course=course, student=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        context['is_editing'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Обновить средний рейтинг курса
        self._update_course_rating()
        
        messages.success(self.request, 'Ваш отзыв обновлен!')
        return response
    
    def _update_course_rating(self):
        """Обновить средний рейтинг и количество отзывов курса"""
        course = self.object.course
        stats = Review.objects.filter(
            course=course,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        course.average_rating = stats['avg_rating'] or 0
        course.total_reviews = stats['total_reviews']
        course.save(update_fields=['average_rating', 'total_reviews'])
    
    def get_success_url(self):
        return reverse('course_detail', kwargs={'slug': self.object.course.slug})


class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """
    Студент удаляет свой отзыв
    """
    model = Review
    template_name = 'courses/reviews/review_confirm_delete.html'
    
    def get_object(self, queryset=None):
        course = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        return get_object_or_404(Review, course=course, student=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context
    
    def delete(self, request, *args, **kwargs):
        course = self.get_object().course
        response = super().delete(request, *args, **kwargs)
        
        # Обновить средний рейтинг курса
        stats = Review.objects.filter(
            course=course,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        course.average_rating = stats['avg_rating'] or 0
        course.total_reviews = stats['total_reviews']
        course.save(update_fields=['average_rating', 'total_reviews'])
        
        messages.success(request, 'Ваш отзыв удален.')
        return response
    
    def get_success_url(self):
        return reverse('course_detail', kwargs={'slug': self.kwargs.get('slug')})


class CourseReviewsView(ListView):
    """
    Все отзывы о курсе (пагинация)
    """
    model = Review
    template_name = 'courses/reviews/course_reviews.html'
    context_object_name = 'reviews'
    paginate_by = 10
    
    def get_queryset(self):
        self.course = get_object_or_404(Course, slug=self.kwargs.get('slug'))
        return Review.objects.filter(
            course=self.course,
            is_approved=True
        ).select_related('student').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        
        # Статистика рейтинга
        stats = Review.objects.filter(
            course=self.course,
            is_approved=True
        ).aggregate(
            avg_rating=Avg('rating'),
            total_reviews=Count('id')
        )
        context['avg_rating'] = stats['avg_rating'] or 0
        context['total_reviews'] = stats['total_reviews']
        
        # Распределение оценок
        rating_distribution = {}
        for i in range(1, 6):
            count = Review.objects.filter(
                course=self.course,
                is_approved=True,
                rating=i
            ).count()
            rating_distribution[i] = count
        context['rating_distribution'] = rating_distribution
        
        # Проверка: пользователь записан и может оставить отзыв
        if self.request.user.is_authenticated:
            context['is_enrolled'] = Enrollment.objects.filter(
                student=self.request.user,
                course=self.course
            ).exists()
            context['user_review'] = Review.objects.filter(
                student=self.request.user,
                course=self.course
            ).first()
        
        return context


# ============================================================
# CERTIFICATE VIEWS (Система сертификатов)
# ============================================================

class MyCertificatesView(LoginRequiredMixin, ListView):
    """
    Список сертификатов студента
    """
    model = Certificate
    template_name = 'courses/certificates/my_certificates.html'
    context_object_name = 'certificates'
    
    def get_queryset(self):
        return Certificate.objects.filter(
            enrollment__student=self.request.user
        ).select_related('enrollment__course').order_by('-issued_at')


class CertificateDetailView(LoginRequiredMixin, DetailView):
    """
    Просмотр сертификата
    """
    model = Certificate
    template_name = 'courses/certificates/certificate_detail.html'
    context_object_name = 'certificate'
    
    def get_object(self, queryset=None):
        certificate_number = self.kwargs.get('certificate_number')
        return get_object_or_404(Certificate, certificate_number=certificate_number)


class CertificateVerifyView(View):
    """
    Публичная проверка подлинности сертификата
    """
    template_name = 'courses/certificates/certificate_verify.html'
    
    def get(self, request, certificate_number=None):
        certificate = None
        searched = False
        
        if certificate_number:
            searched = True
            certificate = Certificate.objects.filter(
                certificate_number=certificate_number
            ).first()
        
        return render(request, self.template_name, {
            'certificate': certificate,
            'searched': searched,
            'certificate_number': certificate_number
        })
    
    def post(self, request):
        certificate_number = request.POST.get('certificate_number', '').strip().upper()
        return redirect('certificate_verify_number', certificate_number=certificate_number)


class CertificatePrintView(LoginRequiredMixin, View):
    """
    Версия сертификата для печати (HTML)
    """
    def get(self, request, certificate_number):
        certificate = get_object_or_404(Certificate, certificate_number=certificate_number)
        
        # Проверка: студент или преподаватель курса
        is_owner = certificate.enrollment.student == request.user
        is_instructor = certificate.enrollment.course.instructor == request.user
        
        if not (is_owner or is_instructor or request.user.is_staff):
            messages.error(request, 'У вас нет доступа к этому сертификату.')
            return redirect('my_courses')
        
        return render(request, 'courses/certificates/certificate_print.html', {
            'certificate': certificate
        })


# ============================================================
# LESSON COMMENT VIEWS (Обсуждения и комментарии)
# ============================================================

class LessonCommentCreateView(LoginRequiredMixin, CreateView):
    """
    Создание комментария к уроку
    """
    model = LessonComment
    form_class = LessonCommentForm
    
    def form_valid(self, form):
        lesson_id = self.kwargs.get('lesson_id')
        lesson = get_object_or_404(Lesson, id=lesson_id)
        course = lesson.section.course
        
        # Проверка: записан ли студент на курс или преподаватель
        is_enrolled = Enrollment.objects.filter(student=self.request.user, course=course).exists()
        is_instructor = course.instructor == self.request.user
        
        if not (is_enrolled or is_instructor):
            messages.error(self.request, 'Вы должны быть записаны на курс, чтобы оставлять комментарии.')
            return redirect('lesson_view', lesson_id=lesson_id)
        
        form.instance.lesson = lesson
        form.instance.author = self.request.user
        
        # Проверить ответ на комментарий
        reply_to_id = self.request.POST.get('reply_to')
        if reply_to_id:
            form.instance.reply_to = get_object_or_404(LessonComment, id=reply_to_id)
        
        messages.success(self.request, 'Комментарий добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        lesson_id = self.kwargs.get('lesson_id')
        return reverse('lesson_view', kwargs={'lesson_id': lesson_id}) + '#comments'


class LessonCommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование комментария
    """
    model = LessonComment
    form_class = LessonCommentForm
    template_name = 'courses/comments/comment_form.html'
    pk_url_kwarg = 'comment_id'
    
    def test_func(self):
        comment = self.get_object()
        return comment.author == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Комментарий обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('lesson_view', kwargs={'lesson_id': self.object.lesson.id}) + '#comments'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.object.lesson
        context['course'] = self.object.lesson.section.course
        return context


class LessonCommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление комментария
    """
    model = LessonComment
    template_name = 'courses/comments/comment_confirm_delete.html'
    pk_url_kwarg = 'comment_id'
    
    def test_func(self):
        comment = self.get_object()
        # Автор или преподаватель курса может удалить
        is_author = comment.author == self.request.user
        is_instructor = comment.lesson.section.course.instructor == self.request.user
        return is_author or is_instructor
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Комментарий удален.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse('lesson_view', kwargs={'lesson_id': self.object.lesson.id}) + '#comments'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.object.lesson
        context['course'] = self.object.lesson.section.course
        return context


class InstructorCommentPinView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Закрепить/открепить комментарий (только преподаватель)
    """
    def test_func(self):
        comment_id = self.kwargs.get('comment_id')
        comment = get_object_or_404(LessonComment, id=comment_id)
        return comment.lesson.section.course.instructor == self.request.user
    
    def post(self, request, comment_id):
        comment = get_object_or_404(LessonComment, id=comment_id)
        comment.is_pinned = not comment.is_pinned
        comment.save()
        
        action = 'закреплен' if comment.is_pinned else 'откреплен'
        messages.success(request, f'Комментарий {action}.')
        return redirect('lesson_view', lesson_id=comment.lesson.id)

# ============================================================
# PAYMENT VIEWS (Система платежей)
# ============================================================

class CourseCheckoutView(LoginRequiredMixin, View):
    """
    Страница оформления покупки курса
    """
    template_name = 'courses/payments/checkout.html'
    
    def get(self, request, slug):
        course = get_object_or_404(Course, slug=slug, status='published')
        
        # Проверка - уже ли записан на курс
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.info(request, f'Вы уже записаны на курс "{course.title}".')
            return redirect('course_detail', slug=course.slug)
        
        # Проверка - уже ли есть активная покупка
        purchase = Purchase.objects.filter(
            student=request.user,
            course=course,
            status__in=['pending', 'completed']
        ).first()
        
        if purchase and purchase.status == 'completed':
            # Если уже оплачено, создать запись
            Enrollment.objects.get_or_create(student=request.user, course=course)
            messages.info(request, f'Вы уже оплатили этот курс.')
            return redirect('course_detail', slug=course.slug)
        
        # Подготовить контекст
        price = course.current_price
        discount_amount = Decimal('0')
        
        form = CheckoutForm()
        
        context = {
            'course': course,
            'price': price,
            'discount_amount': discount_amount,
            'total_amount': price - discount_amount,
            'form': form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '',
            'purchase': purchase,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug, status='published')
        form = CheckoutForm(request.POST)
        
        # Проверка - уже ли записан на курс
        if Enrollment.objects.filter(student=request.user, course=course).exists():
            messages.error(request, 'Вы уже записаны на этот курс.')
            return redirect('course_detail', slug=course.slug)
        
        if form.is_valid():
            payment_method_type = form.cleaned_data['payment_method']
            promo_code_input = form.cleaned_data.get('promo_code', '').strip()
            
            # Применить промокод если есть
            discount_amount = Decimal('0')
            promo_code = None
            
            if promo_code_input:
                try:
                    promo_code = PromoCode.objects.get(code=promo_code_input.upper())
                    if promo_code.is_valid():
                        # Проверить применимость к курсу
                        if promo_code.applicable_courses.exists() and course not in promo_code.applicable_courses.all():
                            messages.error(request, 'Этот промокод не применим к данному курсу.')
                            promo_code = None
                        else:
                            final_price = promo_code.apply_discount(course.current_price)
                            discount_amount = course.current_price - final_price
                            promo_code.current_uses += 1
                            promo_code.save()
                    else:
                        messages.error(request, 'Промокод неактивен или истек.')
                        promo_code = None
                except PromoCode.DoesNotExist:
                    messages.error(request, 'Промокод не найден.')
            
            price = course.current_price
            total_amount = price - discount_amount
            
            # Создать запись о покупке
            purchase, created = Purchase.objects.get_or_create(
                student=request.user,
                course=course,
                defaults={
                    'status': 'pending',
                    'price': price,
                    'discount_amount': discount_amount,
                    'total_amount': total_amount,
                    'promo_code': promo_code_input.upper() if promo_code else '',
                }
            )
            
            if not created and purchase.status != 'pending':
                messages.error(request, 'Ошибка при создании покупки.')
                return redirect('course_detail', slug=course.slug)
            
            # Перенаправить на нужную платежную систему
            if payment_method_type == 'stripe':
                return redirect('stripe_payment', purchase_id=purchase.id)
            elif payment_method_type == 'paypal':
                return redirect('paypal_payment', purchase_id=purchase.id)
            elif payment_method_type == 'yookassa':
                return redirect('yookassa_payment', purchase_id=purchase.id)
        
        # Если форма невалидна, показать ошибку
        messages.error(request, 'Пожалуйста, корректно заполните все поля.')
        return redirect('course_checkout', slug=slug)


class StripePaymentView(LoginRequiredMixin, View):
    """
    Обработка платежа через Stripe
    """
    template_name = 'courses/payments/stripe_payment.html'
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='pending')
        
        context = {
            'purchase': purchase,
            'course': purchase.course,
            'amount': int(purchase.total_amount * 100),  # Stripe требует сумму в центах
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY if hasattr(settings, 'STRIPE_PUBLIC_KEY') else '',
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, purchase_id):
        """
        Обработка платежа (webhook от Stripe приходит сюда)
        """
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='pending')
        
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY if hasattr(settings, 'STRIPE_SECRET_KEY') else ''
            
            # В реальном приложении здесь будет обработка платежа
            # Для MVP используем простую схему
            
            payment, created = Payment.objects.get_or_create(
                purchase=purchase,
                defaults={
                    'amount': purchase.total_amount,
                    'currency': 'RUB',
                    'status': 'pending',
                    'stripe_payment_intent_id': request.POST.get('stripe_payment_intent_id', ''),
                }
            )
            
            # Отметить как успешно
            purchase.status = 'completed'
            purchase.completed_at = timezone.now()
            purchase.save()
            
            payment.status = 'succeeded'
            payment.completed_at = timezone.now()
            payment.save()
            
            # Создать запись на курс
            Enrollment.objects.get_or_create(
                student=request.user,
                course=purchase.course
            )
            
            messages.success(request, f'✓ Платеж успешно обработан! Вы записаны на курс "{purchase.course.title}".')
            return redirect('course_detail', slug=purchase.course.slug)
        
        except Exception as e:
            purchase.status = 'failed'
            purchase.save()
            
            messages.error(request, f'Ошибка при обработке платежа: {str(e)}')
            return redirect('course_checkout', slug=purchase.course.slug)


class PayPalPaymentView(LoginRequiredMixin, View):
    """
    Обработка платежа через PayPal
    """
    template_name = 'courses/payments/paypal_payment.html'
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='pending')
        
        context = {
            'purchase': purchase,
            'course': purchase.course,
        }
        
        return render(request, self.template_name, context)


class YookassaPaymentView(LoginRequiredMixin, View):
    """
    Обработка платежа через Yookassa (Яндекс.Касса)
    """
    template_name = 'courses/payments/yookassa_payment.html'
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='pending')
        
        context = {
            'purchase': purchase,
            'course': purchase.course,
        }
        
        return render(request, self.template_name, context)


class PaymentSuccessView(LoginRequiredMixin, View):
    """
    Страница успешной оплаты
    """
    template_name = 'courses/payments/payment_success.html'
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='completed')
        
        context = {
            'purchase': purchase,
            'course': purchase.course,
        }
        
        return render(request, self.template_name, context)


class PaymentFailedView(LoginRequiredMixin, View):
    """
    Страница ошибки платежа
    """
    template_name = 'courses/payments/payment_failed.html'
    
    def get(self, request, purchase_id):
        purchase = get_object_or_404(Purchase, id=purchase_id, student=request.user, status='failed')
        
        context = {
            'purchase': purchase,
            'course': purchase.course,
        }
        
        return render(request, self.template_name, context)


class PurchaseHistoryView(LoginRequiredMixin, ListView):
    """
    История покупок студента
    """
    model = Purchase
    template_name = 'courses/payments/purchase_history.html'
    context_object_name = 'purchases'
    paginate_by = 10
    
    def get_queryset(self):
        return Purchase.objects.filter(
            student=self.request.user
        ).select_related('course').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_spent'] = sum(p.total_amount for p in self.get_queryset() if p.status == 'completed')
        context['completed_purchases'] = self.get_queryset().filter(status='completed').count()
        return context


class RefundRequestView(LoginRequiredMixin, CreateView):
    """
    Запрос на возврат денежных средств
    """
    model = Refund
    form_class = RefundRequestForm
    template_name = 'courses/payments/refund_request.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.purchase = get_object_or_404(Purchase, id=kwargs.get('purchase_id'), student=request.user, status='completed')
        
        # Проверка - уже ли есть запрос на возврат
        if Refund.objects.filter(purchase=self.purchase, status__in=['pending', 'approved']).exists():
            messages.error(request, 'Вы уже отправили запрос на возврат для этой покупки.')
            return redirect('purchase_history')
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        refund = form.save(commit=False)
        refund.purchase = self.purchase
        refund.student = self.request.user
        refund.refund_amount = self.purchase.total_amount
        refund.save()
        
        messages.success(request, 'Ваш запрос на возврат отправлен. Мы свяжемся с вами в течение 3-5 дней.')
        return redirect('purchase_history')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase'] = self.purchase
        context['course'] = self.purchase.course
        return context
    
    def get_success_url(self):
        return reverse_lazy('purchase_history')


# ============================================================
# MEDIA LIBRARY VIEWS (Медиа-библиотека для преподавателей)
# ============================================================

class MediaLibraryView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    """
    Медиа-библиотека курса - просмотр всех загруженных файлов
    """
    model = CourseMedia
    template_name = 'courses/instructor/media_library.html'
    context_object_name = 'media_files'
    paginate_by = 24
    
    def test_func(self):
        course_slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=course_slug)
        return course.instructor == self.request.user
    
    def get_queryset(self):
        course_slug = self.kwargs.get('slug')
        self.course = get_object_or_404(Course, slug=course_slug)
        
        queryset = CourseMedia.objects.filter(course=self.course)
        
        # Фильтр по типу
        media_type = self.request.GET.get('type')
        if media_type in ['image', 'video', 'document', 'audio', 'other']:
            queryset = queryset.filter(media_type=media_type)
        
        # Поиск
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(original_filename__icontains=search) |
                Q(description__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.course
        context['upload_form'] = CourseMediaUploadForm()
        context['current_type'] = self.request.GET.get('type', '')
        context['search_query'] = self.request.GET.get('q', '')
        
        # Статистика
        all_media = CourseMedia.objects.filter(course=self.course)
        context['total_files'] = all_media.count()
        context['images_count'] = all_media.filter(media_type='image').count()
        context['videos_count'] = all_media.filter(media_type='video').count()
        context['documents_count'] = all_media.filter(media_type='document').count()
        context['total_size'] = sum(m.file_size for m in all_media)
        context['total_size_display'] = self._format_size(context['total_size'])
        
        return context
    
    def _format_size(self, size):
        """Human-readable размер файла"""
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"


class MediaUploadView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Загрузка нового медиа-файла
    """
    model = CourseMedia
    form_class = CourseMediaUploadForm
    template_name = 'courses/instructor/media_upload.html'
    
    def test_func(self):
        course_slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=course_slug)
        return course.instructor == self.request.user
    
    def form_valid(self, form):
        course_slug = self.kwargs.get('slug')
        course = get_object_or_404(Course, slug=course_slug)
        
        form.instance.course = course
        form.instance.uploaded_by = self.request.user
        form.instance.original_filename = form.cleaned_data['file'].name
        
        # Определить MIME-тип
        import mimetypes
        mime_type, _ = mimetypes.guess_type(form.cleaned_data['file'].name)
        form.instance.mime_type = mime_type or 'application/octet-stream'
        
        messages.success(self.request, f'Файл "{form.instance.original_filename}" успешно загружен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('media_library', kwargs={'slug': self.kwargs.get('slug')})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('slug')
        context['course'] = get_object_or_404(Course, slug=course_slug)
        return context


class MediaUploadAjaxView(LoginRequiredMixin, View):
    """
    AJAX загрузка файлов (для drag-and-drop)
    """
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        
        # Проверка прав доступа
        if course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return JsonResponse({'error': 'Файл не предоставлен'}, status=400)
        
        # Проверка размера (50 MB)
        max_size = 50 * 1024 * 1024
        if uploaded_file.size > max_size:
            return JsonResponse({'error': 'Файл слишком большой (макс. 50 MB)'}, status=400)
        
        # Определить MIME-тип
        import mimetypes
        mime_type, _ = mimetypes.guess_type(uploaded_file.name)
        
        # Создать запись
        media = CourseMedia.objects.create(
            course=course,
            uploaded_by=request.user,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            mime_type=mime_type or 'application/octet-stream',
            title=request.POST.get('title', ''),
            description=request.POST.get('description', ''),
        )
        
        return JsonResponse({
            'success': True,
            'id': media.id,
            'filename': media.original_filename,
            'url': media.file.url,
            'media_type': media.media_type,
            'size': media.file_size_display,
            'markdown': media.markdown_embed,
            'html': media.html_embed,
        })


class MediaDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление медиа-файла
    """
    model = CourseMedia
    template_name = 'courses/instructor/media_confirm_delete.html'
    pk_url_kwarg = 'media_id'
    
    def test_func(self):
        media = self.get_object()
        return media.course.instructor == self.request.user
    
    def get_success_url(self):
        return reverse('media_library', kwargs={'slug': self.object.course.slug})
    
    def delete(self, request, *args, **kwargs):
        media = self.get_object()
        filename = media.original_filename
        
        # Удалить файл с диска
        if media.file:
            media.file.delete(save=False)
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Файл "{filename}" удален.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


class MediaDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX удаление файла
    """
    def post(self, request, media_id):
        media = get_object_or_404(CourseMedia, id=media_id)
        
        # Проверка прав доступа
        if media.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        filename = media.original_filename
        
        # Удалить файл с диска
        if media.file:
            media.file.delete(save=False)
        
        media.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Файл "{filename}" удален.'
        })


class MediaGetUrlView(LoginRequiredMixin, View):
    """
    Получить URL и код для вставки медиа-файла
    """
    def get(self, request, media_id):
        media = get_object_or_404(CourseMedia, id=media_id)
        
        # Проверка прав доступа (преподаватель курса)
        if media.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        return JsonResponse({
            'id': media.id,
            'filename': media.original_filename,
            'title': media.title,
            'url': media.file.url,
            'media_type': media.media_type,
            'size': media.file_size_display,
            'markdown': media.markdown_embed,
            'html': media.html_embed,
        })
