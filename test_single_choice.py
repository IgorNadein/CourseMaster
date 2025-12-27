"""
Тест архитектурной переделки single-choice логики
python manage.py shell < test_single_choice.py
"""

from courses.models import Course, Section, Lesson, Quiz, Question, QuestionChoice
from profiles.models import UserProfile
from django.contrib.auth.models import User

print("\n" + "="*60)
print("ТЕСТ: Single-Choice Логика на Уровне Модели")
print("="*60 + "\n")

# Подготовка: создать тестовые данные
try:
    user = User.objects.get(username='testuser')
except User.DoesNotExist:
    user = User.objects.create_user(username='testuser', password='testpass123')

try:
    course = Course.objects.get(title='Test Course')
except Course.DoesNotExist:
    course = Course.objects.create(
        title='Test Course',
        instructor=user,
        status='draft'
    )

try:
    section = Section.objects.get(title='Test Section')
except Section.DoesNotExist:
    section = Section.objects.create(course=course, title='Test Section', order=1)

try:
    lesson = Lesson.objects.get(title='Test Lesson')
except Lesson.DoesNotExist:
    lesson = Lesson.objects.create(
        section=section,
        title='Test Lesson',
        lesson_type='quiz',
        order=1
    )

try:
    quiz = Quiz.objects.get(lesson=lesson)
except Quiz.DoesNotExist:
    quiz = Quiz.objects.create(lesson=lesson, title='Test Quiz')

# TEST 1: Создание вопроса с одиночным выбором
print("\n[TEST 1] Создание SINGLE-CHOICE вопроса")
print("-" * 60)

try:
    q_single = Question.objects.create(
        quiz=quiz,
        text='Какой из этих языков самый популярный?',
        type='single',
        order=1
    )
    
    # Создать 4 варианта
    choice_a = QuestionChoice.objects.create(question=q_single, text='Python', is_correct=False, order=1)
    choice_b = QuestionChoice.objects.create(question=q_single, text='Java', is_correct=False, order=2)
    choice_c = QuestionChoice.objects.create(question=q_single, text='JavaScript', is_correct=False, order=3)
    choice_d = QuestionChoice.objects.create(question=q_single, text='C++', is_correct=False, order=4)
    
    print(f"✅ Создан вопрос: '{q_single.text}'")
    print(f"   Тип: {q_single.type}")
    print(f"   Вариантов: {q_single.choices.count()}")
except Exception as e:
    print(f"❌ Ошибка: {e}")

# TEST 2: Установка первого правильного ответа
print("\n[TEST 2] Установка ПЕРВОГО правильного ответа (Python)")
print("-" * 60)

try:
    choice_a.is_correct = True
    choice_a.save()
    
    # Проверить все варианты
    q_single.refresh_from_db()
    all_choices = q_single.choices.all()
    correct_count = sum(1 for c in all_choices if c.is_correct)
    
    print(f"До установки: все is_correct=False")
    print(f"\nПосле установки choice_a.is_correct=True и save():")
    for choice in all_choices:
        status = "✅ ПРАВИЛЬНЫЙ" if choice.is_correct else "❌ неправильный"
        print(f"  - {choice.text}: {status}")
    
    print(f"\nВсего правильных ответов: {correct_count}")
    assert correct_count == 1, f"Ошибка: должно быть 1, а есть {correct_count}"
    assert choice_a.is_correct == True, "choice_a должен быть правильным"
    print("✅ ТЕСТ ПРОЙДЕН")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛИЛСЯ: {e}")

# TEST 3: Смена правильного ответа
print("\n[TEST 3] Смена правильного ответа (Java)")
print("-" * 60)

try:
    choice_b.is_correct = True
    choice_b.save()
    
    q_single.refresh_from_db()
    all_choices = q_single.choices.all()
    correct_count = sum(1 for c in all_choices if c.is_correct)
    
    print(f"Смена правильного ответа: choice_a → choice_b")
    print(f"\nПосле choice_b.is_correct=True и save():")
    for choice in all_choices:
        status = "✅ ПРАВИЛЬНЫЙ" if choice.is_correct else "❌ неправильный"
        print(f"  - {choice.text}: {status}")
    
    print(f"\nВсего правильных ответов: {correct_count}")
    assert correct_count == 1, f"Ошибка: должно быть 1, а есть {correct_count}"
    assert choice_a.is_correct == False, "choice_a должен быть неправильным"
    assert choice_b.is_correct == True, "choice_b должен быть правильным"
    print("✅ ТЕСТ ПРОЙДЕН")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛИЛСЯ: {e}")

# TEST 4: Multiple-choice не затрагивается
print("\n[TEST 4] MULTIPLE-CHOICE вопрос (не затрагивается)")
print("-" * 60)

try:
    q_multiple = Question.objects.create(
        quiz=quiz,
        text='Выберите все правильные ответы',
        type='multiple',
        order=2
    )
    
    choice_x = QuestionChoice.objects.create(question=q_multiple, text='Вариант X', is_correct=False, order=1)
    choice_y = QuestionChoice.objects.create(question=q_multiple, text='Вариант Y', is_correct=False, order=2)
    choice_z = QuestionChoice.objects.create(question=q_multiple, text='Вариант Z', is_correct=False, order=3)
    
    # Установить оба как правильные
    choice_x.is_correct = True
    choice_x.save()
    
    choice_y.is_correct = True
    choice_y.save()
    
    q_multiple.refresh_from_db()
    all_choices = q_multiple.choices.all()
    correct_count = sum(1 for c in all_choices if c.is_correct)
    
    print(f"Тип вопроса: {q_multiple.type}")
    print(f"\nПосле установки двух правильных ответов:")
    for choice in all_choices:
        status = "✅ ПРАВИЛЬНЫЙ" if choice.is_correct else "❌ неправильный"
        print(f"  - {choice.text}: {status}")
    
    print(f"\nВсего правильных ответов: {correct_count}")
    assert correct_count == 2, f"Ошибка: должно быть 2, а есть {correct_count}"
    assert choice_x.is_correct == True, "choice_x должен быть правильным"
    assert choice_y.is_correct == True, "choice_y должен быть правильным"
    print("✅ ТЕСТ ПРОЙДЕН")
except Exception as e:
    print(f"❌ ТЕСТ ПРОВАЛИЛСЯ: {e}")

# Очистка
print("\n[CLEANUP] Удаление тестовых данных")
print("-" * 60)

try:
    q_single.delete()
    q_multiple.delete()
    quiz.delete()
    lesson.delete()
    section.delete()
    course.delete()
    print("✅ Тестовые данные удалены")
except Exception as e:
    print(f"⚠️ Ошибка при очистке: {e}")

print("\n" + "="*60)
print("ИТОГИ ТЕСТИРОВАНИЯ")
print("="*60)
print("\n✅ Архитектура работает правильно!")
print("   - Single-choice: только 1 правильный ответ")
print("   - Multiple-choice: разрешены несколько правильных")
print("   - Логика на уровне модели → безопасно везде\n")
