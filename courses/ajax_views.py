"""
AJAX API views для современного quiz builder и course builder
"""
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.db import models
from .models import Quiz, Question, QuestionChoice, Course, Section, Lesson, Assignment, Category


class QuizBuilderView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Современный inline quiz builder (как Google Forms)
    """
    model = Quiz
    template_name = 'courses/instructor/quiz_builder.html'
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
        
        return context


class QuizUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновление настроек теста
    """
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Проверка прав доступа
        if quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Валидация полей
        allowed_fields = ['title', 'description', 'pass_percentage', 'attempts_limit', 
                         'time_limit_minutes', 'shuffle_questions', 'show_answers']
        
        for field, value in data.items():
            if field not in allowed_fields:
                return JsonResponse({'error': f'Поле {field} не разрешено'}, status=400)
            
            # Валидация конкретных полей
            if field == 'pass_percentage':
                try:
                    value = int(value)
                    if not 0 <= value <= 100:
                        return JsonResponse({'error': 'Проходной балл должен быть от 0 до 100'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Проходной балл должен быть числом'}, status=400)
            
            elif field == 'attempts_limit':
                try:
                    value = int(value)
                    if value < 1:
                        return JsonResponse({'error': 'Минимум попыток - 1'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Количество попыток должно быть числом'}, status=400)
            
            elif field == 'time_limit_minutes':
                if value:
                    try:
                        value = int(value)
                        if value < 1:
                            return JsonResponse({'error': 'Время должно быть больше 0'}, status=400)
                    except (ValueError, TypeError):
                        return JsonResponse({'error': 'Время должно быть числом'}, status=400)
            
            elif field in ['shuffle_questions', 'show_answers']:
                if not isinstance(value, bool):
                    return JsonResponse({'error': f'{field} должно быть true/false'}, status=400)
            
            # Обновить поле
            if hasattr(quiz, field):
                setattr(quiz, field, value)
        
        quiz.save()
        
        return JsonResponse({'success': True})


class QuestionCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создать новый вопрос
    """
    def post(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)
        
        # Проверка прав доступа
        if quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Валидация типа вопроса
        question_type = data.get('type', 'single')
        valid_types = ['single', 'multiple', 'true_false', 'text']
        if question_type not in valid_types:
            return JsonResponse({'error': f'Тип вопроса должен быть один из: {valid_types}'}, status=400)
        
        # Валидация баллов
        try:
            points = int(data.get('points', 1))
            if points < 1:
                return JsonResponse({'error': 'Баллы должны быть больше 0'}, status=400)
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Баллы должны быть числом'}, status=400)
        
        # Валидация текста вопроса
        text = data.get('text', 'Новый вопрос').strip()
        if not text:
            return JsonResponse({'error': 'Текст вопроса не может быть пустым'}, status=400)
        
        # Определить порядковый номер
        last_question = quiz.questions.order_by('-order').first()
        order = (last_question.order + 1) if last_question else 1
        
        # Создать вопрос
        question = Question.objects.create(
            quiz=quiz,
            text=text,
            type=question_type,
            points=points,
            order=order
        )
        
        # Создать варианты ответов по умолчанию для single/multiple
        if question.type in ['single', 'multiple']:
            for i in range(4):
                QuestionChoice.objects.create(
                    question=question,
                    text=f'Вариант {i+1}',
                    is_correct=False,
                    order=i+1
                )
        
        return JsonResponse({
            'success': True,
            'question_id': question.id
        })


class QuestionUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновить вопрос
    """
    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        
        # Проверка прав доступа
        if question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Валидация полей
        allowed_fields = ['text', 'type', 'points', 'explanation', 'order']
        
        for field, value in data.items():
            if field not in allowed_fields:
                return JsonResponse({'error': f'Поле {field} не разрешено'}, status=400)
            
            # Валидация конкретных полей
            if field == 'text':
                if not value or not value.strip():
                    return JsonResponse({'error': 'Текст вопроса не может быть пустым'}, status=400)
            
            elif field == 'type':
                valid_types = ['single', 'multiple', 'true_false', 'text']
                if value not in valid_types:
                    return JsonResponse({'error': f'Тип должен быть один из: {valid_types}'}, status=400)
            
            elif field == 'points':
                try:
                    value = int(value)
                    if value < 1:
                        return JsonResponse({'error': 'Баллы должны быть больше 0'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Баллы должны быть числом'}, status=400)
            
            elif field == 'order':
                try:
                    value = int(value)
                    if value < 1:
                        return JsonResponse({'error': 'Порядок должен быть больше 0'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Порядок должен быть числом'}, status=400)
            
            # Обновить поле
            if hasattr(question, field):
                setattr(question, field, value)
        
        question.save()
        
        return JsonResponse({'success': True})


class QuestionDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Удалить вопрос
    """
    def delete(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        
        # Проверка прав доступа
        if question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        question.delete()
        
        return JsonResponse({'success': True})


class QuestionDuplicateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Дублировать вопрос со всеми вариантами
    """
    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        
        # Проверка прав доступа
        if question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        # Скопировать вопрос
        choices = list(question.choices.all())
        question.pk = None
        question.text = f"{question.text} (копия)"
        question.order = question.quiz.questions.count() + 1
        question.save()
        
        # Скопировать варианты ответов
        for choice in choices:
            choice.pk = None
            choice.question = question
            choice.save()
        
        return JsonResponse({
            'success': True,
            'question_id': question.id
        })


class ChoiceCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создать вариант ответа
    """
    def post(self, request, question_id):
        question = get_object_or_404(Question, id=question_id)
        
        # Проверка прав доступа
        if question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Валидация текста
        text = data.get('text', '').strip()
        if not text:
            text = f'Вариант {question.choices.count() + 1}'
        
        # Валидация is_correct
        is_correct = data.get('is_correct', False)
        # Конвертировать строку в boolean если нужно
        if isinstance(is_correct, str):
            is_correct = is_correct.lower() in ['true', '1', 'yes']
        elif not isinstance(is_correct, bool):
            return JsonResponse({'error': 'is_correct должно быть true/false'}, status=400)
        
        # Определить порядковый номер
        last_choice = question.choices.order_by('-order').first()
        order = (last_choice.order + 1) if last_choice else 1
        
        # Создать вариант (это вызовет логику в QuestionChoice.save())
        choice = QuestionChoice.objects.create(
            question=question,
            text=text,
            is_correct=is_correct,
            order=order
        )
        
        return JsonResponse({
            'success': True,
            'choice_id': choice.id
        })


class ChoiceUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновить вариант ответа
    """
    def post(self, request, choice_id):
        choice = get_object_or_404(QuestionChoice, id=choice_id)
        
        # Проверка прав доступа
        if choice.question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Валидация полей
        allowed_fields = ['text', 'is_correct', 'order']
        
        for field, value in data.items():
            if field not in allowed_fields:
                return JsonResponse({'error': f'Поле {field} не разрешено'}, status=400)
            
            # Валидация конкретных полей
            if field == 'is_correct':
                # Конвертировать строку в boolean если нужно
                if isinstance(value, str):
                    value = value.lower() in ['true', '1', 'yes']
                elif not isinstance(value, bool):
                    return JsonResponse({'error': 'is_correct должно быть true/false'}, status=400)
            
            elif field == 'order':
                try:
                    value = int(value)
                    if value < 1:
                        return JsonResponse({'error': 'Порядок должен быть больше 0'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Порядок должен быть числом'}, status=400)
            
            # Обновить поле
            if hasattr(choice, field):
                setattr(choice, field, value)
        
        choice.save()  # Это вызовет логику в QuestionChoice.save()
        
        return JsonResponse({'success': True})


class ChoiceDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Удалить вариант ответа
    """
    def delete(self, request, choice_id):
        choice = get_object_or_404(QuestionChoice, id=choice_id)
        
        # Проверка прав доступа
        if choice.question.quiz.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        question = choice.question
        
        # Валидация: должно остаться минимум 2 варианта для single/multiple
        if question.type in ['single', 'multiple']:
            remaining_choices = question.choices.exclude(id=choice_id).count()
            if remaining_choices < 2:
                return JsonResponse({'error': 'Должно остаться минимум 2 варианта ответа'}, status=400)
        
        choice.delete()
        
        return JsonResponse({'success': True})


# ============================================================
# COURSE BUILDER AJAX VIEWS
# ============================================================

class CourseBuilderView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Современный конструктор курса
    """
    model = Course
    template_name = 'courses/instructor/course_builder.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def test_func(self):
        course = self.get_object()
        return course.instructor == self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        
        context['sections'] = course.sections.prefetch_related('lessons').all()
        context['total_lessons'] = Lesson.objects.filter(section__course=course).count()
        context['total_enrollments'] = course.enrollments.count()
        context['categories'] = Category.objects.all()
        
        return context


class CourseUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновление курса
    """
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        if course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Разрешенные поля для обновления
        allowed_fields = ['title', 'subtitle', 'description', 'level', 'language',
                         'duration_hours', 'price', 'discount_price', 'is_free',
                         'preview_video', 'learning_outcomes', 'requirements', 'target_audience']
        
        for field, value in data.items():
            if field == 'category_id':
                if value:
                    try:
                        category = Category.objects.get(id=value)
                        course.category = category
                    except Category.DoesNotExist:
                        return JsonResponse({'error': 'Категория не найдена'}, status=400)
                continue
            
            if field not in allowed_fields:
                continue  # Игнорируем неизвестные поля
            
            if hasattr(course, field):
                setattr(course, field, value)
        
        course.save()
        
        return JsonResponse({'success': True})


class CoursePublishAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Публикация курса
    """
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        if course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        # Проверки перед публикацией
        if not course.sections.exists():
            return JsonResponse({'error': 'Добавьте хотя бы один раздел'}, status=400)
        
        total_lessons = Lesson.objects.filter(section__course=course).count()
        if total_lessons == 0:
            return JsonResponse({'error': 'Добавьте хотя бы один урок'}, status=400)
        
        course.status = 'published'
        course.published_at = timezone.now()
        course.save()
        
        return JsonResponse({'success': True})


class CourseUnpublishAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Снятие курса с публикации
    """
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        if course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        course.status = 'draft'
        course.save()
        
        return JsonResponse({'success': True})


class SectionCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создание раздела
    """
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        
        if course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        title = data.get('title', 'Новый раздел')
        
        # Определить порядковый номер
        last_section = course.sections.order_by('-order').first()
        order = (last_section.order + 1) if last_section else 1
        
        section = Section.objects.create(
            course=course,
            title=title,
            order=order
        )
        
        return JsonResponse({
            'success': True,
            'section_id': section.id,
            'order': order
        })


class SectionUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновление раздела
    """
    def post(self, request, section_id):
        section = get_object_or_404(Section, id=section_id)
        
        if section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        allowed_fields = ['title', 'description', 'order']
        
        for field, value in data.items():
            if field not in allowed_fields:
                continue
            if hasattr(section, field):
                setattr(section, field, value)
        
        section.save()
        
        return JsonResponse({'success': True})


class SectionDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Удаление раздела
    """
    def post(self, request, section_id):
        section = get_object_or_404(Section, id=section_id)
        
        if section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        section.delete()
        
        return JsonResponse({'success': True})


class LessonCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создание урока
    """
    def post(self, request, section_id):
        section = get_object_or_404(Section, id=section_id)
        
        if section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        title = data.get('title', 'Новый урок')
        
        # Определить порядковый номер
        last_lesson = section.lessons.order_by('-order').first()
        order = (last_lesson.order + 1) if last_lesson else 1
        
        lesson = Lesson.objects.create(
            section=section,
            title=title,
            order=order
        )
        
        return JsonResponse({
            'success': True,
            'lesson_id': lesson.id,
            'order': order
        })


class LessonGetAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Получение данных урока
    """
    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        return JsonResponse({
            'success': True,
            'lesson': {
                'id': lesson.id,
                'title': lesson.title,
                'duration_minutes': lesson.duration_minutes,
                'is_preview': lesson.is_preview,
                'order': lesson.order,
                'steps_count': lesson.steps.count()
            }
        })


class LessonUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновление урока
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Неверный формат данных'}, status=400)
        
        # Разрешенные поля (без lesson_type, content, video_url - теперь в Step)
        allowed_fields = ['title', 'duration_minutes', 'is_preview', 'order']
        
        for field, value in data.items():
            if field not in allowed_fields:
                continue
            
            if hasattr(lesson, field):
                setattr(lesson, field, value)
        
        lesson.save()
        
        return JsonResponse({'success': True})


class LessonDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Удаление урока
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        lesson.delete()
        
        return JsonResponse({'success': True})


class QuizCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создание теста для урока
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        # Проверить, нет ли уже теста
        if hasattr(lesson, 'quiz'):
            return JsonResponse({'error': 'Тест уже существует'}, status=400)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        
        quiz = Quiz.objects.create(
            lesson=lesson,
            title=data.get('title', lesson.title),
            pass_percentage=data.get('pass_percentage', 50)
        )
        
        return JsonResponse({
            'success': True,
            'quiz_id': quiz.id
        })


class AssignmentCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создание задания для урока
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        # Проверить, нет ли уже задания
        if hasattr(lesson, 'assignment'):
            return JsonResponse({'error': 'Задание уже существует'}, status=400)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = {}
        
        assignment = Assignment.objects.create(
            lesson=lesson,
            title=data.get('title', lesson.title),
            max_points=data.get('max_points', 100)
        )
        
        return JsonResponse({
            'success': True,
            'assignment_id': assignment.id
        })


class AssignmentGetAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Получить данные задания
    """
    def get(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        if assignment.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        return JsonResponse({
            'success': True,
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'max_points': assignment.max_points,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            }
        })


class AssignmentUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновить задание
    """
    def post(self, request, assignment_id):
        assignment = get_object_or_404(Assignment, id=assignment_id)
        
        if assignment.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Обновить поля
        if 'title' in data:
            assignment.title = data['title']
        if 'description' in data:
            assignment.description = data['description']
        if 'max_points' in data:
            assignment.max_points = int(data['max_points'])
        if 'due_date' in data:
            if data['due_date']:
                from dateutil import parser
                assignment.due_date = parser.parse(data['due_date'])
            else:
                assignment.due_date = None
        
        assignment.save()
        
        return JsonResponse({
            'success': True,
            'assignment': {
                'id': assignment.id,
                'title': assignment.title,
                'description': assignment.description,
                'max_points': assignment.max_points,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            }
        })


# ============================================================
# STEP AJAX VIEWS (Шаги уроков - Stepik-style)
# ============================================================

from .models import Step


class StepListAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Получить список шагов урока
    """
    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Проверка прав доступа
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        steps = lesson.steps.all().order_by('order')
        
        return JsonResponse({
            'success': True,
            'steps': [{
                'id': step.id,
                'step_type': step.step_type,
                'step_type_display': step.get_step_type_display(),
                'title': step.title,
                'order': step.order,
                'points': step.points,
                'is_required': step.is_required,
                'content': step.content,
            } for step in steps]
        })


class StepCreateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Создать новый шаг в уроке
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Проверка прав доступа
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        step_type = data.get('step_type', 'text')
        title = data.get('title', '')
        
        # Валидация типа шага
        valid_types = [choice[0] for choice in Step.STEP_TYPE_CHOICES]
        if step_type not in valid_types:
            return JsonResponse({'error': f'Неверный тип шага: {step_type}'}, status=400)
        
        # Определить order (следующий после максимального)
        max_order = lesson.steps.aggregate(max_order=models.Max('order'))['max_order']
        order = (max_order or -1) + 1
        
        # Создать шаг с дефолтным контентом
        default_content = self._get_default_content(step_type)
        
        step = Step.objects.create(
            lesson=lesson,
            step_type=step_type,
            title=title,
            order=order,
            content=default_content
        )
        
        return JsonResponse({
            'success': True,
            'step': {
                'id': step.id,
                'step_type': step.step_type,
                'step_type_display': step.get_step_type_display(),
                'title': step.title,
                'order': step.order,
                'points': step.points,
                'is_required': step.is_required,
                'content': step.content,
            }
        })
    
    def _get_default_content(self, step_type):
        """Дефолтный контент для разных типов шагов"""
        defaults = {
            'text': {'markdown': '', 'html': ''},
            'video': {'url': '', 'duration': 0, 'source': 'youtube'},
            'quiz_single': {
                'question': 'Введите вопрос...',
                'choices': ['Вариант 1', 'Вариант 2', 'Вариант 3'],
                'correct_index': 0,
                'explanation': ''
            },
            'quiz_multiple': {
                'question': 'Введите вопрос...',
                'choices': ['Вариант 1', 'Вариант 2', 'Вариант 3'],
                'correct_indexes': [0],
                'explanation': ''
            },
            'quiz_sorting': {
                'instruction': 'Расположите элементы в правильном порядке',
                'items': ['Элемент 1', 'Элемент 2', 'Элемент 3'],
                'correct_order': [0, 1, 2]
            },
            'quiz_matching': {
                'instruction': 'Сопоставьте элементы',
                'left': ['Левый 1', 'Левый 2'],
                'right': ['Правый 1', 'Правый 2'],
                'pairs': [[0, 0], [1, 1]]
            },
            'fill_blanks': {
                'text_with_blanks': 'Python — это {{}} язык программирования',
                'answers': ['интерпретируемый']
            },
            'numeric': {
                'question': 'Введите числовой вопрос...',
                'answer': 0,
                'tolerance': 0
            },
            'text_answer': {
                'question': 'Введите вопрос...',
                'patterns': [],
                'case_sensitive': False
            },
            'free_answer': {
                'question': 'Напишите эссе на тему...',
                'min_length': 100,
                'rubric': ''
            },
            'code': {
                'language': 'python',
                'description': 'Описание задачи...',
                'template': '# Ваш код здесь\n',
                'tests': [],
                'time_limit': 5
            },
            'sql': {
                'description': 'Описание SQL-задачи...',
                'database_schema': '',
                'expected_query': '',
                'expected_result': []
            }
        }
        return defaults.get(step_type, {})


class StepGetAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Получить данные шага
    """
    def get(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        
        # Проверка прав доступа
        if step.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        return JsonResponse({
            'success': True,
            'step': {
                'id': step.id,
                'step_type': step.step_type,
                'step_type_display': step.get_step_type_display(),
                'title': step.title,
                'order': step.order,
                'points': step.points,
                'is_required': step.is_required,
                'content': step.content,
            }
        })


class StepUpdateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Обновить шаг
    """
    def post(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        
        # Проверка прав доступа
        if step.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        # Обновить поля
        if 'title' in data:
            step.title = data['title']
        if 'step_type' in data:
            valid_types = [choice[0] for choice in Step.STEP_TYPE_CHOICES]
            if data['step_type'] in valid_types:
                step.step_type = data['step_type']
        if 'points' in data:
            step.points = int(data['points'])
        if 'is_required' in data:
            step.is_required = bool(data['is_required'])
        if 'content' in data:
            step.content = data['content']
        
        step.save()
        
        return JsonResponse({
            'success': True,
            'step': {
                'id': step.id,
                'step_type': step.step_type,
                'step_type_display': step.get_step_type_display(),
                'title': step.title,
                'order': step.order,
                'points': step.points,
                'is_required': step.is_required,
                'content': step.content,
            }
        })


class StepDeleteAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Удалить шаг
    """
    def post(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        
        # Проверка прав доступа
        if step.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        step_title = step.title or f'Шаг {step.order + 1}'
        step.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Шаг "{step_title}" удален'
        })


class StepReorderAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Изменить порядок шагов в уроке
    """
    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, id=lesson_id)
        
        # Проверка прав доступа
        if lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        step_ids = data.get('step_ids', [])
        
        # Обновить порядок
        for index, step_id in enumerate(step_ids):
            Step.objects.filter(id=step_id, lesson=lesson).update(order=index)
        
        return JsonResponse({
            'success': True,
            'message': 'Порядок шагов обновлен'
        })


class StepDuplicateAjaxView(LoginRequiredMixin, View):
    """
    AJAX: Дублировать шаг
    """
    def post(self, request, step_id):
        step = get_object_or_404(Step, id=step_id)
        
        # Проверка прав доступа
        if step.lesson.section.course.instructor != request.user:
            return JsonResponse({'error': 'Нет доступа'}, status=403)
        
        # Определить order для копии
        max_order = step.lesson.steps.aggregate(max_order=models.Max('order'))['max_order']
        new_order = (max_order or 0) + 1
        
        # Создать копию
        new_step = Step.objects.create(
            lesson=step.lesson,
            step_type=step.step_type,
            title=f'{step.title} (копия)' if step.title else '',
            order=new_order,
            points=step.points,
            is_required=step.is_required,
            content=step.content.copy() if isinstance(step.content, dict) else step.content
        )
        
        return JsonResponse({
            'success': True,
            'step': {
                'id': new_step.id,
                'step_type': new_step.step_type,
                'step_type_display': new_step.get_step_type_display(),
                'title': new_step.title,
                'order': new_step.order,
                'points': new_step.points,
                'is_required': new_step.is_required,
                'content': new_step.content,
            }
        })


# ============================================================
# STEP PROGRESS API (Проверка ответов и отметка прогресса)
# ============================================================

class StepCheckAnswerView(LoginRequiredMixin, View):
    """
    AJAX: Проверка ответа студента на интерактивный шаг
    """
    def post(self, request, step_id):
        from .models import Enrollment, StepProgress
        import re
        
        step = get_object_or_404(Step, id=step_id)
        course = step.lesson.section.course
        
        # Проверка записи на курс
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Вы не записаны на этот курс'}, status=403)
        
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный JSON'}, status=400)
        
        # Получить или создать прогресс
        progress, created = StepProgress.objects.get_or_create(
            enrollment=enrollment,
            step=step,
            defaults={'status': 'in_progress'}
        )
        
        # Увеличить счетчик попыток
        progress.attempts += 1
        progress.answer_data = data
        progress.status = 'in_progress'
        
        # Проверка ответа в зависимости от типа шага
        is_correct = False
        message = ''
        explanation = ''
        
        step_type = step.step_type
        content = step.content or {}
        
        if step_type == 'quiz_single':
            # Один правильный ответ
            correct_index = content.get('correct_index', 0)
            selected_index = data.get('selected_index')
            
            is_correct = selected_index == correct_index
            if is_correct:
                message = 'Правильно! ✓'
            else:
                message = 'Неправильно. Попробуйте еще раз.'
            explanation = content.get('explanation', '')
            
        elif step_type == 'quiz_multiple':
            # Несколько правильных ответов
            correct_indexes = set(content.get('correct_indexes', []))
            selected_indexes = set(data.get('selected_indexes', []))
            
            is_correct = correct_indexes == selected_indexes
            if is_correct:
                message = 'Правильно! Все ответы верны. ✓'
            else:
                message = 'Неправильно. Не все ответы выбраны правильно.'
            explanation = content.get('explanation', '')
            
        elif step_type == 'numeric':
            # Числовой ответ с погрешностью
            correct_answer = content.get('answer', 0)
            tolerance = content.get('tolerance', 0)
            user_value = data.get('value', 0)
            
            is_correct = abs(user_value - correct_answer) <= tolerance
            if is_correct:
                message = f'Правильно! Ответ: {correct_answer} ✓'
            else:
                message = 'Неправильно. Попробуйте еще раз.'
            explanation = content.get('explanation', '')
            
        elif step_type == 'text_answer':
            # Текстовый ответ (проверка по паттернам)
            patterns = content.get('patterns', [])
            case_sensitive = content.get('case_sensitive', False)
            user_text = data.get('text', '').strip()
            
            is_correct = False
            for pattern in patterns:
                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    if re.match(pattern, user_text, flags):
                        is_correct = True
                        break
                except re.error:
                    # Если pattern не regex, сравниваем как текст
                    if case_sensitive:
                        is_correct = user_text == pattern
                    else:
                        is_correct = user_text.lower() == pattern.lower()
                    if is_correct:
                        break
            
            if is_correct:
                message = 'Правильно! ✓'
            else:
                message = 'Неправильно. Попробуйте еще раз.'
            explanation = content.get('explanation', '')
            
        elif step_type == 'quiz_sorting':
            # Сортировка
            correct_order = content.get('correct_order', [])
            user_order = data.get('user_order', [])
            
            is_correct = correct_order == user_order
            if is_correct:
                message = 'Правильно! Порядок верный. ✓'
            else:
                message = 'Неправильный порядок. Попробуйте еще раз.'
            
        elif step_type == 'quiz_matching':
            # Сопоставление
            correct_pairs = content.get('pairs', [])
            user_pairs = data.get('pairs', [])
            
            # Преобразуем в set для сравнения
            correct_set = set(tuple(p) for p in correct_pairs)
            user_set = set(tuple(p) for p in user_pairs)
            
            is_correct = correct_set == user_set
            if is_correct:
                message = 'Правильно! Все пары сопоставлены верно. ✓'
            else:
                message = 'Неправильно. Попробуйте еще раз.'
            
        elif step_type == 'fill_blanks':
            # Заполнение пропусков
            correct_answers = content.get('answers', [])
            user_answers = data.get('answers', [])
            
            if len(correct_answers) == len(user_answers):
                all_correct = all(
                    ua.strip().lower() == ca.strip().lower() 
                    for ua, ca in zip(user_answers, correct_answers)
                )
                is_correct = all_correct
            else:
                is_correct = False
            
            if is_correct:
                message = 'Правильно! Все пропуски заполнены верно. ✓'
            else:
                message = 'Неправильно. Попробуйте еще раз.'
            
        elif step_type == 'free_answer':
            # Свободный ответ (эссе) - не проверяется автоматически
            min_length = content.get('min_length', 0)
            user_text = data.get('text', '').strip()
            
            if len(user_text) >= min_length:
                is_correct = True  # Просто принимаем ответ
                message = 'Ваш ответ отправлен на проверку преподавателю.'
                progress.status = 'in_progress'  # Ждет проверки
            else:
                is_correct = False
                message = f'Ответ слишком короткий. Минимум {min_length} символов.'
            
        elif step_type == 'code':
            # Код - пока просто принимаем (полная проверка требует интеграции с sandbox)
            user_code = data.get('code', '')
            if user_code.strip():
                is_correct = True
                message = 'Код отправлен на проверку.'
                progress.status = 'in_progress'  # Ждет проверки (или sandbox)
            else:
                is_correct = False
                message = 'Напишите код для проверки.'
        
        # Сохранить результат
        progress.is_correct = is_correct
        if is_correct:
            progress.completed = True
            progress.completed_at = timezone.now()
            progress.status = 'completed'
            progress.score = step.points
            progress.max_score = step.points
        
        progress.save()
        
        return JsonResponse({
            'success': True,
            'is_correct': is_correct,
            'message': message,
            'explanation': explanation if not is_correct else '',
            'attempts': progress.attempts,
            'completed': progress.completed,
        })


class StepCompleteView(LoginRequiredMixin, View):
    """
    AJAX: Отметить шаг (text/video) как пройденный
    """
    def post(self, request, step_id):
        from .models import Enrollment, StepProgress
        
        step = get_object_or_404(Step, id=step_id)
        course = step.lesson.section.course
        
        # Проверка записи на курс
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
        except Enrollment.DoesNotExist:
            return JsonResponse({'error': 'Вы не записаны на этот курс'}, status=403)
        
        # Только для контентных шагов (text, video)
        if step.is_interactive:
            return JsonResponse({'error': 'Этот шаг требует ответа'}, status=400)
        
        # Получить или создать прогресс
        progress, created = StepProgress.objects.get_or_create(
            enrollment=enrollment,
            step=step,
            defaults={'status': 'not_started'}
        )
        
        # Отметить как пройденный
        progress.completed = True
        progress.completed_at = timezone.now()
        progress.status = 'completed'
        progress.score = step.points
        progress.max_score = step.points
        progress.save()
        
        # Проверить завершение урока
        all_steps = step.lesson.steps.all()
        completed_steps = StepProgress.objects.filter(
            enrollment=enrollment,
            step__in=all_steps,
            completed=True
        ).count()
        
        lesson_completed = completed_steps == all_steps.count()
        
        return JsonResponse({
            'success': True,
            'completed': True,
            'lesson_completed': lesson_completed,
            'steps_completed': completed_steps,
            'steps_total': all_steps.count(),
        })

