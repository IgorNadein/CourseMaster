# Очистка старого кода (28.12.2025)

## Описание
Удаление устаревших views, URLs и шаблонов, которые были заменены новыми AJAX-based конструкторами.

## Удалённые Views (из courses/views.py)

### Section/Lesson Views (~180 строк)
- `SectionCreateView` - создание раздела
- `SectionUpdateView` - редактирование раздела  
- `SectionDeleteView` - удаление раздела
- `LessonCreateView` - создание урока
- `LessonUpdateView` - редактирование урока
- `LessonDeleteView` - удаление урока

**Заменены на:** `CourseBuilderView` + AJAX API (`SectionCreateAjaxView`, `SectionUpdateAjaxView`, `SectionDeleteAjaxView`, `LessonCreateAjaxView`, `LessonUpdateAjaxView`, `LessonDeleteAjaxView`)

### Question/Choice Views (~240 строк)
- `QuestionCreateView` - создание вопроса
- `QuestionDetailView` - детали вопроса
- `QuestionUpdateView` - редактирование вопроса
- `QuestionDeleteView` - удаление вопроса
- `QuestionChoiceCreateView` - создание варианта ответа
- `QuestionChoiceUpdateView` - редактирование варианта
- `QuestionChoiceDeleteView` - удаление варианта

**Заменены на:** `QuizBuilderView` + AJAX API (`QuestionCreateAjaxView`, `QuestionUpdateAjaxView`, `QuestionDeleteAjaxView`, `ChoiceCreateAjaxView`, `ChoiceUpdateAjaxView`, `ChoiceDeleteAjaxView`)

## Удалённые URLs (из courses/urls.py)

```python
# Разделы (удалены)
path('instructor/course/<slug:course_slug>/section/create/', ...)
path('instructor/section/<int:section_id>/edit/', ...)
path('instructor/section/<int:section_id>/delete/', ...)

# Уроки (удалены)
path('instructor/section/<int:section_id>/lesson/create/', ...)
path('instructor/lesson/<int:lesson_id>/edit/', ...)
path('instructor/lesson/<int:lesson_id>/delete/', ...)

# Вопросы (удалены)
path('instructor/quiz/<int:quiz_id>/question/create/', ...)
path('instructor/question/<int:question_id>/', ...)
path('instructor/question/<int:question_id>/edit/', ...)
path('instructor/question/<int:question_id>/delete/', ...)

# Варианты ответов (удалены)
path('instructor/question/<int:question_id>/choice/create/', ...)
path('instructor/choice/<int:choice_id>/edit/', ...)
path('instructor/choice/<int:choice_id>/delete/', ...)
```

## Удалённые шаблоны (templates/courses/instructor/)

Ранее удалены (в предыдущей сессии):
- `section_form.html`
- `section_confirm_delete.html`
- `lesson_form.html`
- `lesson_confirm_delete.html`
- `quiz_form.html`
- `quiz_detail.html`
- `question_form.html`
- `question_detail.html`
- `choice_form.html`
- `choice_confirm_delete.html`

## Обновлённые шаблоны

### course_detail.html
- Удалены кнопки "Добавить раздел", "Добавить урок", "Редактировать/Удалить"
- Добавлены ссылки на `course_builder` для управления контентом
- Шаблон теперь служит для просмотра статистики и быстрого доступа к конструктору

### assignment_form.html
- Заменена ссылка `lesson_update` → `course_builder`

### assignment_detail.html
- Заменена ссылка `lesson_update` → `course_builder`

## Новая архитектура

### Конструктор курсов (CourseBuilder)
- **URL**: `/courses/instructor/course/<slug>/builder/`
- **Шаблон**: `course_builder.html`
- **CSS**: `course-builder.css`
- **AJAX API**: 12 endpoints в `ajax_views.py`

### Конструктор тестов (QuizBuilder)
- **URL**: `/courses/instructor/quiz/<id>/builder/`
- **Шаблон**: `quiz_builder.html`  
- **CSS**: `quiz-builder.css`
- **AJAX API**: 9 endpoints в `ajax_views.py`

## Результат

- Кодовая база стала чище и легче поддерживать
- Удалено ~420 строк устаревшего кода views
- Удалено ~13 старых URL patterns
- Удалено 10 устаревших шаблонов
- Все ссылки обновлены на новые endpoints
- Django check: ✅ no issues
