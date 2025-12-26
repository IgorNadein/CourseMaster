from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from courses.models import Category, Course, Section, Lesson


class Command(BaseCommand):
    help = 'Создает тестовые данные для платформы CourseMaster'

    def handle(self, *args, **options):
        # Очистить старые данные (опционально)
        # Category.objects.all().delete()
        # Course.objects.all().delete()
        
        # Создать категории
        categories_data = [
            {'name': 'Программирование', 'icon': '💻', 'description': 'Курсы по программированию и разработке'},
            {'name': 'Бизнес', 'icon': '💼', 'description': 'Курсы по бизнесу и предпринимательству'},
            {'name': 'Маркетинг', 'icon': '📊', 'description': 'Курсы по маркетингу и аналитике'},
            {'name': 'Дизайн', 'icon': '🎨', 'description': 'Курсы по дизайну и творчеству'},
            {'name': 'Личное развитие', 'icon': '🚀', 'description': 'Курсы по саморазвитию'},
        ]
        
        categories = {}
        for cat_data in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slugify(cat_data['name']),
                defaults={
                    'name': cat_data['name'],
                    'icon': cat_data['icon'],
                    'description': cat_data['description']
                }
            )
            categories[cat_data['name']] = cat
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Категория "{cat_data["name"]}" создана'))
            else:
                self.stdout.write(f'ℹ Категория "{cat_data["name"]}" уже существует')
        
        # Получить или создать преподавателя
        instructor, created = User.objects.get_or_create(
            username='teacher',
            defaults={
                'first_name': 'Иван',
                'last_name': 'Петров',
                'email': 'teacher@example.com'
            }
        )
        
        if created:
            instructor.set_password('password123')
            instructor.save()
            self.stdout.write(self.style.SUCCESS(f'✓ Преподаватель "{instructor.username}" создан'))
        else:
            self.stdout.write(f'ℹ Преподаватель "{instructor.username}" уже существует')
        
        # Создать курсы
        courses_data = [
            {
                'title': 'Python для начинающих',
                'subtitle': 'Полный курс Python с нуля до профессионала',
                'description': 'В этом курсе вы научитесь основам программирования на Python. Курс включает практические примеры и проекты.',
                'category': 'Программирование',
                'level': 'beginner',
                'price': 2990.00,
                'duration_hours': 40,
                'status': 'published',
                'learning_outcomes': 'Основные концепции Python\nРаботу с переменными и типами данных\nЦиклы и условные операторы\nРаботу с функциями\nОбъектно-ориентированное программирование',
                'requirements': 'Компьютер с установленным Python\nБазовое понимание английского языка\nОтношение к программированию\nВремя для практики',
            },
            {
                'title': 'Django: создание веб-приложений',
                'subtitle': 'Разработка современных веб-приложений на Django',
                'description': 'Практический курс по разработке веб-приложений с использованием фреймворка Django. Мы создадим несколько проектов в процессе обучения.',
                'category': 'Программирование',
                'level': 'intermediate',
                'price': 3990.00,
                'duration_hours': 50,
                'status': 'published',
                'learning_outcomes': 'Архитектура Django приложений\nМодели и базы данных\nViews и URL маршруты\nШаблоны Django\nФормы и валидация\nАутентификация и авторизация',
                'requirements': 'Знание Python\nПонимание HTTP протокола\nБазовые знания SQL\nЖелание разрабатывать веб-приложения',
            },
            {
                'title': 'JavaScript для веб-разработчиков',
                'subtitle': 'Овладейте JavaScript и создавайте интерактивные веб-сайты',
                'description': 'Полный курс JavaScript для начинающих веб-разработчиков. Учим современный JavaScript (ES6+) и популярные библиотеки.',
                'category': 'Программирование',
                'level': 'beginner',
                'price': 2490.00,
                'duration_hours': 35,
                'status': 'published',
                'learning_outcomes': 'Основы JavaScript\nDOM и манипуляция элементами\nAsynchronous JavaScript (Promises, async/await)\nREST API\nJavaScript фреймворки (React основы)',
                'requirements': 'Знание HTML и CSS\nТекстовый редактор\nБраузер с DevTools\nЛюбопытство к веб-разработке',
            },
            {
                'title': 'Стартап с нуля',
                'subtitle': 'От идеи к запуску собственного стартапа',
                'description': 'Курс для предпринимателей, которые хотят запустить свой собственный бизнес. Мы рассмотрим все этапы от идеи до первых клиентов.',
                'category': 'Бизнес',
                'level': 'beginner',
                'price': 4990.00,
                'duration_hours': 45,
                'status': 'published',
                'learning_outcomes': 'Поиск бизнес-идеи\nАнализ рынка и конкурентов\nСоздание бизнес-плана\nПривлечение первых клиентов\nМасштабирование бизнеса',
                'requirements': 'Желание открыть бизнес\nВремя на реализацию идеи\nБаза знаний в выбранной области\nМотивация',
            },
            {
                'title': 'Основы цифрового маркетинга',
                'subtitle': 'Научитесь продавать в интернете',
                'description': 'Практический курс по цифровому маркетингу. Изучим SMM, контент-маркетинг, SEO и аналитику.',
                'category': 'Маркетинг',
                'level': 'beginner',
                'price': 1990.00,
                'duration_hours': 25,
                'status': 'published',
                'learning_outcomes': 'Основы digital маркетинга\nСоциальные сети (SMM)\nКонтент-маркетинг\nSEO основы\nEmail маркетинг\nАналитика и метрики',
                'requirements': 'Базовое понимание интернета\nПоля для экспериментов\nАккаунты в социальных сетях\nЖелание учиться',
            },
            {
                'title': 'Основы Figma',
                'subtitle': 'Создавайте уникальные дизайны в Figma',
                'description': 'Курс по дизайну в Figma - инструменте для создания интерфейсов и логотипов. Практические примеры и проекты.',
                'category': 'Дизайн',
                'level': 'beginner',
                'price': 2290.00,
                'duration_hours': 20,
                'status': 'published',
                'learning_outcomes': 'Интерфейс Figma\nОсновные инструменты рисования\nРаботу со слоями и компонентами\nСоздание прототипов\nСотрудничество в команде',
                'requirements': 'Компьютер с доступом в интернет\nЗаписанный аккаунт в Figma\nБазовое понимание дизайна\nТворческое мышление',
            },
        ]
        
        courses = {}
        for course_data in courses_data:
            category = categories[course_data.pop('category')]
            course_slug = slugify(course_data['title'])
            course, created = Course.objects.get_or_create(
                slug=course_slug,
                defaults={
                    'instructor': instructor,
                    'category': category,
                    **course_data
                }
            )
            courses[course.title] = course
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Курс "{course.title}" создан'))
            else:
                self.stdout.write(f'ℹ Курс "{course.title}" уже существует')
        
        # Создать разделы и уроки для каждого курса
        course_structure = {
            'Python для начинающих': [
                {
                    'title': 'Введение в Python',
                    'lessons': [
                        {'title': 'Что такое Python?', 'type': 'video', 'duration': 15},
                        {'title': 'Установка Python', 'type': 'article', 'duration': 10},
                        {'title': 'Hello, World!', 'type': 'video', 'duration': 20},
                    ]
                },
                {
                    'title': 'Переменные и типы данных',
                    'lessons': [
                        {'title': 'Переменные', 'type': 'video', 'duration': 25},
                        {'title': 'Строки', 'type': 'video', 'duration': 20},
                        {'title': 'Числа', 'type': 'video', 'duration': 15},
                        {'title': 'Списки и кортежи', 'type': 'video', 'duration': 30},
                    ]
                },
                {
                    'title': 'Условные операторы и циклы',
                    'lessons': [
                        {'title': 'If-else операторы', 'type': 'video', 'duration': 25},
                        {'title': 'Цикл for', 'type': 'video', 'duration': 20},
                        {'title': 'Цикл while', 'type': 'video', 'duration': 15},
                        {'title': 'Практика', 'type': 'assignment', 'duration': 60},
                    ]
                },
            ],
            'Django: создание веб-приложений': [
                {
                    'title': 'Введение в Django',
                    'lessons': [
                        {'title': 'Что такое Django?', 'type': 'video', 'duration': 20},
                        {'title': 'Установка и настройка', 'type': 'video', 'duration': 15},
                        {'title': 'Создание первого проекта', 'type': 'video', 'duration': 25},
                    ]
                },
                {
                    'title': 'Модели и базы данных',
                    'lessons': [
                        {'title': 'ORM в Django', 'type': 'video', 'duration': 30},
                        {'title': 'Создание моделей', 'type': 'video', 'duration': 25},
                        {'title': 'Миграции', 'type': 'video', 'duration': 20},
                    ]
                },
            ],
        }
        
        for course_title, sections_data in course_structure.items():
            course = courses.get(course_title)
            if not course:
                continue
            
            for section_idx, section_data in enumerate(sections_data, 1):
                section, created = Section.objects.get_or_create(
                    course=course,
                    title=section_data['title'],
                    defaults={'order': section_idx}
                )
                
                if created:
                    self.stdout.write(f'  ✓ Раздел "{section.title}" в курсе "{course.title}" создан')
                
                for lesson_idx, lesson_data in enumerate(section_data['lessons'], 1):
                    lesson_type_map = {
                        'video': 'video',
                        'article': 'article',
                        'assignment': 'assignment',
                        'quiz': 'quiz'
                    }
                    
                    lesson, created = Lesson.objects.get_or_create(
                        section=section,
                        title=lesson_data['title'],
                        defaults={
                            'lesson_type': lesson_type_map.get(lesson_data['type'], 'video'),
                            'duration_minutes': lesson_data['duration'],
                            'order': lesson_idx,
                            'is_preview': lesson_idx == 1,  # Первый урок бесплатный
                            'content': f'Содержание урока: {lesson_data["title"]}'
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'    ✓ Урок "{lesson.title}" создан')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Тестовые данные успешно созданы!'))
        self.stdout.write(f'\n📊 Статистика:')
        self.stdout.write(f'  - Категорий: {Category.objects.count()}')
        self.stdout.write(f'  - Курсов: {Course.objects.count()}')
        self.stdout.write(f'  - Разделов: {Section.objects.count()}')
        self.stdout.write(f'  - Уроков: {Lesson.objects.count()}')
        
        self.stdout.write(f'\n👤 Данные для входа:')
        self.stdout.write(f'  - Username: teacher')
        self.stdout.write(f'  - Password: password123')
