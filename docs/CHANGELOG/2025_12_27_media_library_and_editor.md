# Changelog: Медиа-библиотека и Улучшенный редактор уроков

**Дата:** 27 декабря 2025  
**Фаза:** 3.5 - Course Constructor & Media Library  
**Статус:** ✅ Завершено

---

## 📋 Обзор изменений

Добавлена полноценная медиа-библиотека для преподавателей и улучшен редактор уроков с toolbar и live preview.

---

## 🆕 Новые компоненты

### 1. Модель CourseMedia

**Файл:** `courses/models.py`

```python
class CourseMedia(models.Model):
    """
    Медиа-файл курса (изображения, видео, документы)
    """
    MEDIA_TYPE_CHOICES = [
        ('image', 'Изображение'),
        ('video', 'Видео'),
        ('document', 'Документ'),
        ('audio', 'Аудио'),
        ('other', 'Другое'),
    ]
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='media_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_media')
    file = models.FileField(upload_to='courses/media/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default='other')
    file_size = models.PositiveIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    # ...
```

**Функции:**
- Автоматическое определение типа медиа по расширению файла
- Свойства для отображения: `file_size_display`, `is_image`, `is_video`
- Готовые embed-коды: `markdown_embed`, `html_embed`

### 2. Views для медиа-библиотеки

**Файл:** `courses/views.py`

| View | Назначение |
|------|-----------|
| `MediaLibraryView` | Список всех медиа-файлов курса с пагинацией, фильтрацией и поиском |
| `MediaUploadView` | Страница загрузки файла |
| `MediaUploadAjaxView` | AJAX endpoint для drag-and-drop загрузки |
| `MediaDeleteView` | Страница подтверждения удаления |
| `MediaDeleteAjaxView` | AJAX удаление |
| `MediaGetUrlView` | Получение URL и embed-кодов файла |

### 3. URL Patterns

**Файл:** `courses/urls.py`

```python
# Медиа-библиотека (Преподаватели)
path('instructor/course/<slug:slug>/media/', views.MediaLibraryView.as_view(), name='media_library'),
path('instructor/course/<slug:slug>/media/upload/', views.MediaUploadView.as_view(), name='media_upload'),
path('instructor/course/<slug:slug>/media/upload/ajax/', views.MediaUploadAjaxView.as_view(), name='media_upload_ajax'),
path('instructor/media/<int:media_id>/delete/', views.MediaDeleteView.as_view(), name='media_delete'),
path('instructor/media/<int:media_id>/delete/ajax/', views.MediaDeleteAjaxView.as_view(), name='media_delete_ajax'),
path('instructor/media/<int:media_id>/url/', views.MediaGetUrlView.as_view(), name='media_get_url'),
```

### 4. Формы

**Файл:** `courses/forms.py`

- `CourseMediaUploadForm` - Загрузка файла с валидацией (макс. 50 MB, разрешенные расширения)
- `CourseMediaEditForm` - Редактирование метаданных файла

---

## 🎨 Новые шаблоны

### `templates/courses/instructor/media_library.html`

Полноценная медиа-библиотека с:
- Dropzone для drag-and-drop загрузки
- Фильтрация по типу файла (изображения, видео, документы)
- Поиск по названию и описанию
- Сетка карточек с превью
- Кнопки копирования Markdown и URL
- Модальные окна для загрузки и удаления
- Toast-уведомления

### `templates/courses/instructor/media_upload.html`

Страница загрузки нового файла.

### `templates/courses/instructor/media_confirm_delete.html`

Страница подтверждения удаления файла.

### `templates/courses/instructor/lesson_form.html` (Обновлен)

Улучшенный редактор уроков:
- Двухколоночный layout (редактор + preview)
- Toolbar с кнопками форматирования
- Live preview Markdown
- Ссылка на медиа-библиотеку
- Модальное окно с Markdown-шпаргалкой

---

## 📁 Новые статические файлы

### CSS

| Файл | Назначение |
|------|-----------|
| `static/css/media-library.css` | Стили медиа-библиотеки (dropzone, карточки, анимации) |
| `static/css/lesson-editor.css` | Стили редактора уроков (toolbar, preview) |

### JavaScript

| Файл | Назначение |
|------|-----------|
| `static/js/media-library.js` | Drag-and-drop загрузка, AJAX операции, копирование в буфер |
| `static/js/lesson-editor.js` | Toolbar actions, live preview, keyboard shortcuts |

---

## 🛠️ Django Admin

**Файл:** `courses/admin.py`

Добавлен `CourseMediaAdmin` с:
- Превью миниатюр для изображений
- Отображение типа и размера файла
- Фильтрация по курсу и типу медиа
- Inline предпросмотр файлов

---

## 📊 Миграции

- `0009_coursemedia.py` - Создание таблицы CourseMedia

---

## ✅ Функциональные возможности

### Медиа-библиотека

1. ✅ Загрузка файлов (изображения, видео, документы до 50 MB)
2. ✅ Drag-and-drop загрузка с AJAX
3. ✅ Автоматическое определение типа файла
4. ✅ Фильтрация по типу (изображения/видео/документы)
5. ✅ Поиск по названию и описанию
6. ✅ Копирование Markdown-кода в буфер
7. ✅ Копирование URL в буфер
8. ✅ Удаление файлов с подтверждением
9. ✅ Статистика (количество файлов, общий размер)
10. ✅ Пагинация (24 файла на страницу)

### Редактор уроков

1. ✅ Toolbar с кнопками форматирования:
   - Жирный (Ctrl+B)
   - Курсив (Ctrl+I)
   - Заголовок
   - Ссылка (Ctrl+K)
   - Изображение
   - Блок кода
   - Список
   - Цитата
2. ✅ Live preview с клиентским Markdown-парсером
3. ✅ Keyboard shortcuts (Ctrl+B, Ctrl+I, Ctrl+K, Tab)
4. ✅ Прямая ссылка на медиа-библиотеку
5. ✅ Markdown-шпаргалка в модальном окне

---

## 🧪 Тестирование

- ✅ Все 85 тестов проходят
- ✅ Django system check: no issues
- ✅ Миграции успешно применены

---

## 📝 Как использовать

### Для преподавателя:

1. Перейти в панель управления курсом
2. Нажать кнопку "Медиа" для открытия медиа-библиотеки
3. Загрузить файлы через dropzone или кнопку "Загрузить"
4. Скопировать Markdown-код нужного файла
5. При редактировании урока вставить код в редактор
6. Использовать toolbar для форматирования текста
7. Проверять результат в панели предпросмотра

---

## 🔗 Связанные файлы

- [courses/models.py](../../courses/models.py) - Модель CourseMedia
- [courses/views.py](../../courses/views.py) - Views медиа-библиотеки
- [courses/urls.py](../../courses/urls.py) - URL patterns
- [courses/forms.py](../../courses/forms.py) - Формы загрузки
- [courses/admin.py](../../courses/admin.py) - Admin integration
- [templates/courses/instructor/media_library.html](../../templates/courses/instructor/media_library.html)
- [templates/courses/instructor/lesson_form.html](../../templates/courses/instructor/lesson_form.html)
- [static/css/media-library.css](../../static/css/media-library.css)
- [static/js/media-library.js](../../static/js/media-library.js)
- [static/css/lesson-editor.css](../../static/css/lesson-editor.css)
- [static/js/lesson-editor.js](../../static/js/lesson-editor.js)

---

**Автор:** CourseMaster AI Assistant  
**Версия:** 1.0
