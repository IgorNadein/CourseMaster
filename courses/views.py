from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .models import (Course, Category, Enrollment, Section, Lesson, LessonProgress, Review, 
                     Quiz, Question, QuestionChoice, QuizAttempt, UserAnswer)
from .forms import CourseForm, SectionForm, LessonForm, CoursePublishForm, QuizForm, QuestionForm, QuestionChoiceForm


class CourseListView(ListView):
    """
    Каталог курсов для студентов с фильтрацией и поиском
    """
    model = Course
    template_name = 'courses/course_list.html'
    context_object_name = 'courses'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Course.objects.filter(status='published').select_related(
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
    template_name = 'courses/course_detail.html'
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
    template_name = 'courses/my_courses.html'
    context_object_name = 'enrollments'
    paginate_by = 10
    
    def get_queryset(self):
        return Enrollment.objects.filter(
            student=self.request.user
        ).select_related(
            'course__instructor', 'course__category'
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
        
        return context


class LessonView(LoginRequiredMixin, DetailView):
    """
    Просмотр урока (только для записанных студентов)
    """
    model = Lesson
    template_name = 'courses/lesson_view.html'
    context_object_name = 'lesson'
    pk_url_kwarg = 'lesson_id'
    
    def get_queryset(self):
        return Lesson.objects.select_related(
            'section__course__instructor'
        ).prefetch_related(
            'section__lessons'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = self.object
        course = lesson.section.course
        
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
        
        # Данные курса и раздела
        context['course'] = course
        context['section'] = lesson.section
        
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
        if Enrollment.objects.filter(student=self.request.user, course=course).exists():
            enrollment = Enrollment.objects.get(student=self.request.user, course=course)
            lesson_progress, _ = LessonProgress.objects.get_or_create(
                enrollment=enrollment,
                lesson=lesson
            )
            context['lesson_progress'] = lesson_progress
            context['is_completed'] = lesson_progress.completed
        
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
        messages.success(
            self.request,
            'Курс успешно создан! Теперь добавьте разделы и уроки.'
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.slug})


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
        return reverse('instructor_course_detail', kwargs={'slug': self.object.slug})


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


class InstructorCourseDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Детальная страница курса для преподавателя с управлением
    """
    model = Course
    template_name = 'courses/instructor/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        # Разделы и уроки
        context['sections'] = course.sections.prefetch_related('lessons').all()
        
        # Статистика
        context['total_sections'] = course.sections.count()
        context['total_lessons'] = Lesson.objects.filter(section__course=course).count()
        context['total_enrollments'] = course.enrollments.count()
        
        # Средний прогресс студентов
        enrollments = course.enrollments.all()
        if enrollments:
            avg_progress = sum(e.progress_percentage for e in enrollments) / len(enrollments)
            context['avg_student_progress'] = avg_progress
        else:
            context['avg_student_progress'] = 0
        
        return context


class SectionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Создание раздела курса
    """
    model = Section
    form_class = SectionForm
    template_name = 'courses/instructor/section_form.html'
    
    def test_func(self):
        course_slug = self.kwargs.get('course_slug')
        course = get_object_or_404(Course, slug=course_slug)
        return course.instructor == self.request.user
    
    def form_valid(self, form):
        course_slug = self.kwargs.get('course_slug')
        form.instance.course = get_object_or_404(Course, slug=course_slug)
        messages.success(self.request, 'Раздел успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs.get('course_slug')
        context['course'] = get_object_or_404(Course, slug=course_slug)
        return context


class SectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование раздела
    """
    model = Section
    form_class = SectionForm
    template_name = 'courses/instructor/section_form.html'
    pk_url_kwarg = 'section_id'
    
    def test_func(self):
        section = self.get_object()
        return section.course.instructor == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Раздел успешно обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['course'] = self.object.course
        return context


class SectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление раздела
    """
    model = Section
    template_name = 'courses/instructor/section_confirm_delete.html'
    pk_url_kwarg = 'section_id'
    
    def test_func(self):
        section = self.get_object()
        return section.course.instructor == self.request.user
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.course.slug})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Раздел успешно удален.')
        return super().delete(request, *args, **kwargs)


class LessonCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Создание урока
    """
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/instructor/lesson_form.html'
    
    def test_func(self):
        section_id = self.kwargs.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        return section.course.instructor == self.request.user
    
    def form_valid(self, form):
        section_id = self.kwargs.get('section_id')
        form.instance.section = get_object_or_404(Section, id=section_id)
        messages.success(self.request, 'Урок успешно создан!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.section.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_id = self.kwargs.get('section_id')
        section = get_object_or_404(Section, id=section_id)
        context['section'] = section
        context['course'] = section.course
        return context


class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Редактирование урока
    """
    model = Lesson
    form_class = LessonForm
    template_name = 'courses/instructor/lesson_form.html'
    pk_url_kwarg = 'lesson_id'
    
    def test_func(self):
        lesson = self.get_object()
        return lesson.section.course.instructor == self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Урок успешно обновлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.section.course.slug})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['section'] = self.object.section
        context['course'] = self.object.section.course
        return context


class LessonDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Удаление урока
    """
    model = Lesson
    template_name = 'courses/instructor/lesson_confirm_delete.html'
    pk_url_kwarg = 'lesson_id'
    
    def test_func(self):
        lesson = self.get_object()
        return lesson.section.course.instructor == self.request.user
    
    def get_success_url(self):
        return reverse('instructor_course_detail', kwargs={'slug': self.object.section.course.slug})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Урок успешно удален.')
        return super().delete(request, *args, **kwargs)


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
    template_name = 'courses/quiz_take.html'
    
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
    template_name = 'courses/quiz_results.html'
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


class QuestionCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    Преподаватель добавляет вопрос в тест
    """
    model = Question
    form_class = QuestionForm
    template_name = 'courses/instructor/question_form.html'
    
    def test_func(self):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        return quiz.lesson.section.course.instructor == self.request.user
    
    def form_valid(self, form):
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        form.instance.quiz = quiz
        form.instance.order = quiz.questions.count() + 1
        messages.success(self.request, 'Вопрос добавлен!')
        return super().form_valid(form)
    
    def get_success_url(self):
        quiz_id = self.kwargs.get('quiz_id')
        return reverse('instructor_quiz_detail', kwargs={'quiz_id': quiz_id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quiz_id = self.kwargs.get('quiz_id')
        quiz = get_object_or_404(Quiz, id=quiz_id)
        context['quiz'] = quiz
        context['lesson'] = quiz.lesson
        context['course'] = quiz.lesson.section.course
        return context
