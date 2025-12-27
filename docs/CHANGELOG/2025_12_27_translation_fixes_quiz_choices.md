# Translation Fixes - Quiz and Model Choices

**Дата:** 27 декабря 2025  
**Автор:** AI Assistant  
**Тип изменения:** Translation / Localization  
**Статус:** ✅ Завершено

---

## 📋 Описание

Перевод всех CHOICES и help_text в моделях courses/models.py на русский язык для полной локализации пользовательского интерфейса.

## ❌ Проблема

Пользователь при тестировании системы тестов обнаружил, что часть контента отображается на английском языке:
- Dropdown с типами вопросов показывал "Multiple Choice", "Single Choice", "True/False", "Short Answer"
- Dropdown с уровнями курсов показывал "Beginner", "Intermediate", "Advanced"
- Dropdown с типами уроков показывал "Video", "Article", "Quiz", "Assignment"
- Dropdown со статусами заданий показывал "Submitted", "Graded", "Returned for revision"
- Help text в формах отображался на английском

## ✅ Решение

### Файлы изменены:
- **courses/models.py** - переведены все CHOICES и help_text

### Переводы:

#### 1. **Question.QUESTION_TYPE_CHOICES** (строки 258-263)
```python
# Было:
QUESTION_TYPE_CHOICES = [
    ('multiple', 'Multiple Choice'),
    ('single', 'Single Choice'),
    ('true_false', 'True/False'),
    ('text', 'Short Answer'),
]

# Стало:
QUESTION_TYPE_CHOICES = [
    ('multiple', 'Множественный выбор'),
    ('single', 'Одиночный выбор'),
    ('true_false', 'Правда/Ложь'),
    ('text', 'Текстовый ответ'),
]
```

#### 2. **Course.LEVEL_CHOICES** и **Course.STATUS_CHOICES** (строки 37-47)
```python
# Было:
LEVEL_CHOICES = [
    ('beginner', 'Beginner'),
    ('intermediate', 'Intermediate'),
    ('advanced', 'Advanced'),
]

STATUS_CHOICES = [
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
]

# Стало:
LEVEL_CHOICES = [
    ('beginner', 'Начинающий'),
    ('intermediate', 'Средний'),
    ('advanced', 'Продвинутый'),
]

STATUS_CHOICES = [
    ('draft', 'Черновик'),
    ('published', 'Опубликован'),
    ('archived', 'Архив'),
]
```

#### 3. **Lesson.LESSON_TYPE_CHOICES** (строки 149-154)
```python
# Было:
LESSON_TYPE_CHOICES = [
    ('video', 'Video'),
    ('article', 'Article'),
    ('quiz', 'Quiz'),
    ('assignment', 'Assignment'),
]

# Стало:
LESSON_TYPE_CHOICES = [
    ('video', 'Видео'),
    ('article', 'Статья'),
    ('quiz', 'Тест'),
    ('assignment', 'Задание'),
]
```

#### 4. **AssignmentSubmission.STATUS_CHOICES** (строки 359-363)
```python
# Было:
STATUS_CHOICES = [
    ('submitted', 'Submitted'),
    ('graded', 'Graded'),
    ('returned', 'Returned for revision'),
]

# Стало:
STATUS_CHOICES = [
    ('submitted', 'Отправлено'),
    ('graded', 'Оценено'),
    ('returned', 'Возвращено на доработку'),
]
```

#### 5. **Quiz model help_text** (строки 237-247)
```python
# Было:
pass_percentage = models.PositiveIntegerField(default=50, help_text="Minimum % to pass")
time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Quiz time limit in minutes")
attempts_limit = models.PositiveIntegerField(default=3, help_text="Maximum attempts allowed")
show_answers = models.BooleanField(default=True, help_text="Show correct answers after completion")

# Стало:
pass_percentage = models.PositiveIntegerField(default=50, help_text="Минимальный % для прохождения")
time_limit_minutes = models.PositiveIntegerField(null=True, blank=True, help_text="Лимит времени на тест в минутах")
attempts_limit = models.PositiveIntegerField(default=3, help_text="Максимальное количество попыток")
show_answers = models.BooleanField(default=True, help_text="Показывать правильные ответы после завершения")
```

#### 6. **Question model help_text** (строки 269-271)
```python
# Было:
points = models.PositiveIntegerField(default=1, help_text="Points for correct answer")
explanation = models.TextField(blank=True, help_text="Explanation shown after answer")

# Стало:
points = models.PositiveIntegerField(default=1, help_text="Баллы за правильный ответ")
explanation = models.TextField(blank=True, help_text="Объяснение, показываемое после ответа")
```

## 🎯 Результат

✅ Все dropdown списки в формах теперь отображают русский текст  
✅ Help text в админке Django также переведен на русский  
✅ Пользовательский интерфейс полностью локализован  
✅ Улучшен UX для русскоязычных пользователей  

## 📊 Изменения по файлам

| Файл | Строки | Изменения |
|------|--------|-----------|
| courses/models.py | 37-47 | Course.LEVEL_CHOICES и STATUS_CHOICES |
| courses/models.py | 149-154 | Lesson.LESSON_TYPE_CHOICES |
| courses/models.py | 237-247 | Quiz help_text (4 поля) |
| courses/models.py | 258-263 | Question.QUESTION_TYPE_CHOICES |
| courses/models.py | 269-271 | Question help_text (2 поля) |
| courses/models.py | 359-363 | AssignmentSubmission.STATUS_CHOICES |

**Всего:** 6 блоков изменений, 27 переведенных строк

## 🚀 Миграции

**Не требуются** - изменения затрагивают только отображаемый текст (choices labels и help_text), без изменения структуры БД.

## ✅ Тестирование

1. ✅ Проверено отображение в Django Admin
2. ✅ Проверено отображение в формах (QuizForm, QuestionForm, CourseForm)
3. ✅ Проверено отображение dropdown списков
4. ⏳ Ожидается подтверждение от пользователя

## 📝 Примечания

- Перевод выполнен в соответствии с общей локализацией проекта
- Все термины согласованы с существующими переводами
- Help text переведен для улучшения UX в админке Django

---

**Время выполнения:** ~15 минут  
**Связанные задачи:** Quiz System Integration (Phase 3.5)  
**Следующий шаг:** Проверка пользователем полной локализации
