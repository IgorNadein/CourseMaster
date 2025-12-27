"""
AJAX API views для современного quiz builder и course builder
"""
import json
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.generic import View, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
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
        lesson_type = data.get('lesson_type', 'video')
        
        if lesson_type not in ['video', 'article', 'quiz', 'assignment']:
            return JsonResponse({'error': 'Неверный тип урока'}, status=400)
        
        # Определить порядковый номер
        last_lesson = section.lessons.order_by('-order').first()
        order = (last_lesson.order + 1) if last_lesson else 1
        
        lesson = Lesson.objects.create(
            section=section,
            title=title,
            lesson_type=lesson_type,
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
                'lesson_type': lesson.lesson_type,
                'content': lesson.content,
                'video_url': lesson.video_url,
                'duration_minutes': lesson.duration_minutes,
                'is_preview': lesson.is_preview,
                'order': lesson.order
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
        
        allowed_fields = ['title', 'lesson_type', 'content', 'video_url', 
                         'duration_minutes', 'is_preview', 'order']
        
        for field, value in data.items():
            if field not in allowed_fields:
                continue
            
            if field == 'lesson_type' and value not in ['video', 'article', 'quiz', 'assignment']:
                return JsonResponse({'error': 'Неверный тип урока'}, status=400)
            
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

