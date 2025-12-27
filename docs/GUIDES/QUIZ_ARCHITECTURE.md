# Quiz System Architecture - Диаграмма и документация

## 🏗️ Архитектура

```
ПРЕПОДАВАТЕЛЬ
    │
    ├─→ Создает урок типа "quiz" (LessonCreateView?type=quiz)
    │   └─→ lesson_form.html + lesson_create view
    │
    ├─→ Создает тест (InstructorQuizCreateView)
    │   ├─→ quiz_form.html
    │   ├─→ Сохраняет: title, pass_percentage, attempts_limit, time_limit...
    │   └─→ Редирект на InstructorQuizDetailView
    │
    ├─→ Добавляет вопросы (QuestionCreateView)
    │   ├─→ question_form.html с inline formset для вариантов
    │   ├─→ Выбирает тип: single, multiple, true_false, text
    │   ├─→ Добавляет варианты ответов (QuestionChoice)
    │   ├─→ Отмечает правильные ответы
    │   └─→ Сохраняет баллы и объяснение
    │
    └─→ Публикует курс
        └─→ Студенты могут видеть курс и записаться


СТУДЕНТ
    │
    ├─→ Записывается на курс (CourseEnrollView)
    │   └─→ Enrollment создается
    │
    ├─→ Открывает урок (LessonView)
    │   ├─→ lesson_view.html показывает тип "Тест"
    │   └─→ Кнопка "Пройти тест"
    │
    ├─→ Проходит тест (QuizTakeView GET)
    │   ├─→ quiz_take.html
    │   ├─→ QuizAttempt создается
    │   ├─→ Все вопросы загружаются
    │   ├─→ Варианты ответов показываются
    │   └─→ Студент отвечает на каждый вопрос
    │
    ├─→ Отправляет ответы (QuizTakeView POST)
    │   ├─→ UserAnswer создается для каждого вопроса
    │   ├─→ Для single/multiple/true_false: автоматическая проверка
    │   ├─→ Для text: маркируется для ручной проверки
    │   ├─→ Рассчитываются баллы
    │   ├─→ Определяется passed/failed
    │   └─→ QuizAttempt сохраняется с результатами
    │
    ├─→ Видит результаты (QuizResultsView)
    │   ├─→ quiz_results.html
    │   ├─→ Показывает: score, percentage, is_passed
    │   ├─→ Показывает правильные ответы (если enabled)
    │   ├─→ Показывает объяснения к вопросам
    │   └─→ Опция: пройти тест еще раз (если есть попытки)
    │
    └─→ Может пройти тест повторно (max attempts_limit раз)
```

---

## 📊 Database Schema

```
Quiz (1-to-1 к Lesson)
├─ lesson_id: FK (Lesson)
├─ title: CharField
├─ description: TextField
├─ pass_percentage: PositiveInt (default=50)
├─ time_limit_minutes: PositiveInt (nullable)
├─ attempts_limit: PositiveInt (default=3)
├─ shuffle_questions: Boolean
├─ show_answers: Boolean
└─ created_at, updated_at

    ↓
    
Question (M-to-1 к Quiz)
├─ quiz_id: FK (Quiz)
├─ type: CharField (single/multiple/true_false/text)
├─ text: TextField
├─ points: PositiveInt (default=1)
├─ order: PositiveInt
├─ explanation: TextField (nullable)
└─ created_at

    ├─→ QuestionChoice (M-to-1 к Question)
    │  ├─ question_id: FK (Question)
    │  ├─ text: CharField
    │  ├─ is_correct: Boolean
    │  ├─ order: PositiveInt
    │  └─ created_at
    │
    └─→ UserAnswer (M-to-1 к Question от QuizAttempt)
       ├─ attempt_id: FK (QuizAttempt)
       ├─ question_id: FK (Question)
       ├─ choice_id: FK (QuestionChoice, nullable)
       ├─ text_answer: TextField (nullable)
       ├─ is_correct: Boolean (nullable)
       ├─ points_earned: DecimalField (nullable)
       └─ answered_at


QuizAttempt (M-to-1 к Quiz от Student)
├─ student_id: FK (User)
├─ quiz_id: FK (Quiz)
├─ started_at: DateTime
├─ completed_at: DateTime (nullable)
├─ score: DecimalField (nullable)
├─ total_points: PositiveInt (nullable)
├─ percentage: DecimalField (nullable)
├─ is_passed: Boolean (nullable)
└─ Unique(student, quiz) - одна попытка на студента
```

---

## 🔄 Workflow: Создание теста

### 1. Преподаватель создает новый урок

```
URL: /courses/instructor/section/<section_id>/lesson/create/?type=quiz
Method: GET/POST

GET: lesson_form.html показывается с предзаполненным type='quiz'
POST: 
  - Создается Lesson(lesson_type='quiz')
  - Редирект на instructor_course_detail
  - Кнопка "Создать тест" появляется в списке уроков
```

**Форма (lesson_form.html)**:
- title* (требуется)
- lesson_type = 'quiz' (предзаполнено)
- content (опционально - описание)
- duration_minutes (опционально)
- is_preview (галочка)

---

### 2. Преподаватель создает тест

```
URL: /courses/instructor/lesson/<lesson_id>/quiz/create/
Method: GET/POST

GET: quiz_form.html
POST:
  - Создается Quiz(lesson=lesson)
  - Редирект на instructor_quiz_detail
```

**Форма (quiz_form.html)**:
```html
<form method="post">
  {{ form.title }}              <!-- Название теста -->
  {{ form.description }}        <!-- Описание -->
  {{ form.pass_percentage }}    <!-- Порог прохождения: 70% -->
  {{ form.time_limit_minutes }} <!-- Время: 30 мин (опционально) -->
  {{ form.attempts_limit }}     <!-- Попытки: 3 -->
  {{ form.shuffle_questions }}  <!-- Галочка: перемешивать -->
  {{ form.show_answers }}       <!-- Галочка: показывать ответы -->
  <button>Создать тест</button>
</form>
```

---

### 3. Преподаватель добавляет вопросы

```
URL: /courses/instructor/quiz/<quiz_id>/question/create/
Method: GET/POST

GET: question_form.html
POST:
  - Создается Question(quiz=quiz, order=max_order+1)
  - Если выбран тип с вариантами - inline formset для QuestionChoice
  - Редирект на instructor_quiz_detail
```

**Форма (question_form.html)**:
```html
<form method="post">
  {{ form.type }}         <!-- Dropdown: single, multiple, true_false, text -->
  {{ form.text }}         <!-- Текст вопроса -->
  {{ form.points }}       <!-- Баллы (default=1) -->
  {{ form.order }}        <!-- Порядок (auto-calculated) -->
  {{ form.explanation }}  <!-- Объяснение ответа -->
  
  {% if form.type != 'text' %}
    <!-- Inline formset для вариантов ответов -->
    {{ formset }}  <!-- QuestionChoiceFormSet -->
    
    <div class="choice-form">
      <input name="choices-0-text" placeholder="Вариант ответа">
      <input type="checkbox" name="choices-0-is_correct"> Правильный?
      <input name="choices-0-order" value="1">
    </div>
    <button>Добавить вариант</button>
  {% endif %}
  
  <button>Сохранить вопрос</button>
</form>
```

---

## 🎮 Workflow: Прохождение теста

### 1. Студент открывает тест

```
URL: /courses/quiz/<quiz_id>/take/
Method: GET

GET:
  - Проверить: студент записан на курс
  - Проверить: есть ли попытки (attempts <= attempts_limit)
  - Создать QuizAttempt(student=user, quiz=quiz)
  - Загрузить все Question'ы для этого Quiz
  - Рендерить quiz_take.html
```

**Шаблон (quiz_take.html)**:
```html
<div class="quiz-header">
  <h2>{{ quiz.title }}</h2>
  <p>Порог прохождения: {{ quiz.pass_percentage }}%</p>
  {% if quiz.time_limit_minutes %}
    <p>Время: <span id="timer">{{ quiz.time_limit_minutes }}:00</span></p>
  {% endif %}
</div>

<form method="post" action="{% url 'quiz_take' quiz.id %}">
  {% for question in questions %}
    <div class="question">
      <h4>{{ forloop.counter }}. {{ question.text }}</h4>
      
      {% if question.type == 'single' %}
        <!-- Single choice - radio buttons -->
        {% for choice in question.choices.all %}
          <label>
            <input type="radio" name="question_{{ question.id }}" value="{{ choice.id }}">
            {{ choice.text }}
          </label>
        {% endfor %}
        
      {% elif question.type == 'multiple' %}
        <!-- Multiple choice - checkboxes -->
        {% for choice in question.choices.all %}
          <label>
            <input type="checkbox" name="question_{{ question.id }}" value="{{ choice.id }}">
            {{ choice.text }}
          </label>
        {% endfor %}
        
      {% elif question.type == 'true_false' %}
        <!-- True/False -->
        <label>
          <input type="radio" name="question_{{ question.id }}" value="true">
          Да
        </label>
        <label>
          <input type="radio" name="question_{{ question.id }}" value="false">
          Нет
        </label>
        
      {% elif question.type == 'text' %}
        <!-- Text answer -->
        <textarea name="question_{{ question.id }}" placeholder="Введите ответ"></textarea>
      {% endif %}
    </div>
  {% endfor %}
  
  <button type="submit">Отправить тест</button>
</form>
```

---

### 2. Студент отправляет ответы

```
URL: /courses/quiz/<quiz_id>/take/
Method: POST

POST:
  1. Для каждого Question'а:
     - Получить выбранный ответ (choice_id или text_answer)
     - Создать UserAnswer(attempt=attempt, question=question)
     
  2. Обработать ответы:
     - Для single/multiple/true_false:
       - Получить QuestionChoice.is_correct
       - Установить UserAnswer.is_correct = True/False
       - Рассчитать points_earned = question.points если correct, иначе 0
     - Для text:
       - Установить UserAnswer.is_correct = None (ручная проверка)
       - Установить points_earned = None
     
  3. Рассчитать результаты:
     - total_points = sum(question.points for all questions)
     - earned_points = sum(useranswer.points_earned where is_correct=True)
     - percentage = (earned_points / total_points) * 100
     - is_passed = percentage >= quiz.pass_percentage
     
  4. Обновить QuizAttempt:
     - completed_at = now()
     - score = earned_points
     - total_points = total_points
     - percentage = percentage
     - is_passed = is_passed
     
  5. Редирект на quiz_results
```

---

### 3. Студент видит результаты

```
URL: /courses/quiz/attempt/<attempt_id>/results/
Method: GET

GET:
  - Получить QuizAttempt
  - Получить все UserAnswer'ы для этой попытки
  - Рендерить quiz_results.html
```

**Шаблон (quiz_results.html)**:
```html
<div class="quiz-results">
  <h2>Результаты теста</h2>
  
  <div class="score">
    <h3>Ваш результат: {{ attempt.score }}/{{ attempt.total_points }}</h3>
    <h3>Процент: {{ attempt.percentage }}%</h3>
    <h3 class="{% if attempt.is_passed %}passed{% else %}failed{% endif %}">
      {% if attempt.is_passed %}✓ Тест пройден{% else %}✗ Тест не пройден{% endif %}
    </h3>
  </div>
  
  {% if quiz.show_answers %}
    <div class="answers">
      {% for answer in attempt.answers.all %}
        <div class="answer">
          <h4>{{ answer.question.text }}</h4>
          
          <p><strong>Ваш ответ:</strong> 
            {% if answer.choice %}
              {{ answer.choice.text }}
            {% elif answer.text_answer %}
              {{ answer.text_answer }}
            {% else %}
              (нет ответа)
            {% endif %}
          </p>
          
          <p><strong>Правильный ответ:</strong>
            {% for choice in answer.question.choices.all %}
              {% if choice.is_correct %}
                {{ choice.text }}
              {% endif %}
            {% endfor %}
          </p>
          
          {% if answer.is_correct %}
            <p class="correct">✓ Правильно (+{{ answer.points_earned }} баллов)</p>
          {% elif answer.is_correct == False %}
            <p class="incorrect">✗ Неправильно (0 баллов)</p>
          {% else %}
            <p class="pending">⏳ Ожидает проверки преподавателем</p>
          {% endif %}
          
          <p><em>{{ answer.question.explanation }}</em></p>
        </div>
      {% endfor %}
    </div>
  {% endif %}
  
  {% if attempt.quiz.attempts_limit > 1 %}
    <a href="{% url 'quiz_take' attempt.quiz.id %}" class="btn">
      Пройти тест еще раз
    </a>
  {% endif %}
</div>
```

---

## 🔐 Проверки безопасности

### 1. При создании теста

```python
def test_func(self):
    lesson = Lesson.objects.get(id=lesson_id)
    # Только преподаватель этого курса может создать тест
    return lesson.section.course.instructor == request.user
```

### 2. При прохождении теста

```python
# Проверить: студент записан на курс
enrollment = Enrollment.objects.get(student=request.user, course=course)

# Проверить: тест еще не пройден (или есть попытки)
attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz)
if attempts.count() >= quiz.attempts_limit:
    raise PermissionDenied()
```

### 3. При просмотре результатов

```python
def get_queryset(self):
    # Студент видит только свои результаты
    return QuizAttempt.objects.filter(student=request.user)
```

---

## 📈 Статистика и аналитика

### Для преподавателя

На странице InstructorQuizDetailView показать:
- Количество студентов, прошедших тест
- Средний процент правильных ответов
- Самый сложный вопрос (% правильных ответов)
- Самый легкий вопрос

```python
total_attempts = quiz.attempts.count()
passed_attempts = quiz.attempts.filter(is_passed=True).count()

for question in quiz.questions.all():
    correct_answers = UserAnswer.objects.filter(
        question=question, is_correct=True
    ).count()
    difficulty = (correct_answers / total_attempts) * 100
```

### Для студента

На странице QuizResultsView показать:
- Сравнение с классом (класс получил 65%, вы 82%)
- Рекомендации для улучшения

---

## 🐛 Типичные ошибки и решения

| Проблема | Причина | Решение |
|----------|---------|---------|
| "Нельзя создать тест" | Урок не типа quiz | Убедиться что lesson_type='quiz' |
| "Не добавляются варианты" | Не выбран тип вопроса | Выбрать тип в question_form |
| "Нет ответа на question_form" | FormSet не инициализирован | Передать formset в контекст view |
| "Ошибка при отправке ответов" | Неправильный формат данных | Проверить POST параметры |
| "Результаты не показываются" | quiz.show_answers = False | Установить True в quiz_form |

---

## 🚀 Performance

- **Загрузка вопросов**: prefetch_related('questions__choices')
- **Загрузка ответов**: select_related('attempt__quiz')
- **Рендеринг результатов**: prefetch_related('answers__choice__question')

Оптимизация запросов критична если в тесте 100+ вопросов!

---

**Версия**: 1.0  
**Дата**: 27 декабря 2025  
**Статус**: Актуально для v0.9.6
