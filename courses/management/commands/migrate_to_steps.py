"""
Management command для миграции существующих уроков в Step-формат.

Выполняет:
1. Видео уроки -> Step (type=video)
2. Статьи -> Step (type=text)
3. Тесты (Quiz) -> Step[] (type=quiz_single/quiz_multiple)
4. Задания (Assignment) -> Step (type=free_answer)

Использование:
    python manage.py migrate_to_steps           # Показать что будет мигрировано
    python manage.py migrate_to_steps --execute # Выполнить миграцию
    python manage.py migrate_to_steps --reset   # Удалить все Step и мигрировать заново
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from courses.models import (
    Lesson, Quiz, Question, QuestionChoice, Assignment, Step
)


class Command(BaseCommand):
    help = 'Мигрирует существующие уроки в Step-формат'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--execute',
            action='store_true',
            help='Выполнить миграцию (без этого флага - только показать план)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Удалить все существующие Step перед миграцией',
        )
    
    def handle(self, *args, **options):
        execute = options['execute']
        reset = options['reset']
        
        if reset and execute:
            self.stdout.write(self.style.WARNING('🗑️  Удаление всех существующих Step...'))
            deleted_count = Step.objects.all().delete()[0]
            self.stdout.write(self.style.SUCCESS(f'   Удалено: {deleted_count} шагов'))
        
        # Собираем статистику
        stats = {
            'video': 0,
            'article': 0,
            'quiz': 0,
            'quiz_questions': 0,
            'assignment': 0,
            'skipped': 0,
        }
        
        lessons_to_migrate = []
        
        # Анализ уроков
        for lesson in Lesson.objects.select_related('section__course').prefetch_related('steps'):
            # Пропускаем уроки, у которых уже есть шаги
            if lesson.steps.exists():
                stats['skipped'] += 1
                continue
            
            if lesson.lesson_type == 'video':
                stats['video'] += 1
                lessons_to_migrate.append(('video', lesson))
            
            elif lesson.lesson_type == 'article':
                stats['article'] += 1
                lessons_to_migrate.append(('article', lesson))
            
            elif lesson.lesson_type == 'quiz':
                stats['quiz'] += 1
                # Считаем вопросы в связанном Quiz
                if hasattr(lesson, 'quiz') and lesson.quiz:
                    question_count = lesson.quiz.questions.count()
                    stats['quiz_questions'] += question_count
                lessons_to_migrate.append(('quiz', lesson))
            
            elif lesson.lesson_type == 'assignment':
                stats['assignment'] += 1
                lessons_to_migrate.append(('assignment', lesson))
        
        # Показываем план миграции
        self.stdout.write('')
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('📋 ПЛАН МИГРАЦИИ В STEP-ФОРМАТ'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write('')
        
        self.stdout.write(f'🎬 Видео уроков:     {stats["video"]} → {stats["video"]} Step (type=video)')
        self.stdout.write(f'📝 Статей:           {stats["article"]} → {stats["article"]} Step (type=text)')
        self.stdout.write(f'✅ Тестов:           {stats["quiz"]} → {stats["quiz_questions"]} Step (type=quiz_*)')
        self.stdout.write(f'📋 Заданий:          {stats["assignment"]} → {stats["assignment"]} Step (type=free_answer)')
        self.stdout.write(f'⏭️  Уже мигрировано: {stats["skipped"]}')
        self.stdout.write('')
        
        total_steps = stats['video'] + stats['article'] + stats['quiz_questions'] + stats['assignment']
        self.stdout.write(self.style.SUCCESS(f'📊 Итого будет создано: {total_steps} шагов'))
        self.stdout.write('')
        
        if not execute:
            self.stdout.write(self.style.WARNING('⚠️  Это был предварительный просмотр.'))
            self.stdout.write(self.style.WARNING('   Для выполнения миграции запустите:'))
            self.stdout.write(self.style.WARNING('   python manage.py migrate_to_steps --execute'))
            return
        
        # Выполняем миграцию
        self.stdout.write(self.style.HTTP_INFO('🚀 Выполнение миграции...'))
        self.stdout.write('')
        
        created_steps = 0
        
        with transaction.atomic():
            for lesson_type, lesson in lessons_to_migrate:
                if lesson_type == 'video':
                    created = self._migrate_video_lesson(lesson)
                    created_steps += created
                
                elif lesson_type == 'article':
                    created = self._migrate_article_lesson(lesson)
                    created_steps += created
                
                elif lesson_type == 'quiz':
                    created = self._migrate_quiz_lesson(lesson)
                    created_steps += created
                
                elif lesson_type == 'assignment':
                    created = self._migrate_assignment_lesson(lesson)
                    created_steps += created
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Миграция завершена! Создано {created_steps} шагов.'))
    
    def _migrate_video_lesson(self, lesson):
        """Мигрирует видео урок -> Step (type=video)"""
        content = {
            'url': lesson.video_url or '',
            'duration': lesson.duration_minutes * 60 if lesson.duration_minutes else 0,
            'source': self._detect_video_source(lesson.video_url),
        }
        
        step = Step.objects.create(
            lesson=lesson,
            step_type='video',
            order=0,
            title=lesson.title,
            content=content,
            points=0,
            is_required=True,
        )
        
        self.stdout.write(f'  🎬 Видео: {lesson.title[:50]}')
        return 1
    
    def _detect_video_source(self, url):
        """Определяет источник видео по URL"""
        if not url:
            return 'unknown'
        url = url.lower()
        if 'youtube.com' in url or 'youtu.be' in url:
            return 'youtube'
        elif 'vimeo.com' in url:
            return 'vimeo'
        elif 'rutube.ru' in url:
            return 'rutube'
        return 'direct'
    
    def _migrate_article_lesson(self, lesson):
        """Мигрирует статью -> Step (type=text)"""
        content = {
            'html': lesson.content or '',
            'markdown': '',  # Можно добавить конвертацию HTML->Markdown
        }
        
        step = Step.objects.create(
            lesson=lesson,
            step_type='text',
            order=0,
            title=lesson.title,
            content=content,
            points=0,
            is_required=True,
        )
        
        self.stdout.write(f'  📝 Статья: {lesson.title[:50]}')
        return 1
    
    def _migrate_quiz_lesson(self, lesson):
        """Мигрирует Quiz урок -> несколько Step (type=quiz_single/quiz_multiple)"""
        if not hasattr(lesson, 'quiz') or not lesson.quiz:
            self.stdout.write(self.style.WARNING(f'  ⚠️ Quiz не найден: {lesson.title}'))
            return 0
        
        quiz = lesson.quiz
        questions = quiz.questions.prefetch_related('choices').order_by('order')
        created = 0
        
        for order, question in enumerate(questions):
            choices = list(question.choices.order_by('order'))
            
            # Определяем тип: single или multiple
            correct_count = sum(1 for c in choices if c.is_correct)
            
            if question.type == 'multiple' or correct_count > 1:
                step_type = 'quiz_multiple'
                correct_indexes = [i for i, c in enumerate(choices) if c.is_correct]
                content = {
                    'question': question.text,
                    'choices': [c.text for c in choices],
                    'correct_indexes': correct_indexes,
                    'explanation': question.explanation or '',
                }
            else:
                step_type = 'quiz_single'
                correct_index = next((i for i, c in enumerate(choices) if c.is_correct), 0)
                content = {
                    'question': question.text,
                    'choices': [c.text for c in choices],
                    'correct_index': correct_index,
                    'explanation': question.explanation or '',
                }
            
            step = Step.objects.create(
                lesson=lesson,
                step_type=step_type,
                order=order,
                title=f'Вопрос {order + 1}',
                content=content,
                points=question.points,
                is_required=True,
            )
            created += 1
        
        self.stdout.write(f'  ✅ Quiz: {lesson.title[:40]} -> {created} вопросов')
        return created
    
    def _migrate_assignment_lesson(self, lesson):
        """Мигрирует Assignment урок -> Step (type=free_answer)"""
        if not hasattr(lesson, 'assignment') or not lesson.assignment:
            # Если Assignment не найден, создаём пустой free_answer step
            content = {
                'question': lesson.content or 'Выполните задание и опишите результат.',
                'min_length': 100,
                'rubric': '',
            }
        else:
            assignment = lesson.assignment
            content = {
                'question': assignment.description or lesson.content or 'Выполните задание.',
                'min_length': 50,
                'rubric': f'Максимум баллов: {assignment.max_points}',
                'max_points': assignment.max_points,
            }
        
        step = Step.objects.create(
            lesson=lesson,
            step_type='free_answer',
            order=0,
            title=lesson.title,
            content=content,
            points=content.get('max_points', 10),
            is_required=True,
        )
        
        self.stdout.write(f'  📋 Assignment: {lesson.title[:50]}')
        return 1
