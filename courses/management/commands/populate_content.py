from django.core.management.base import BaseCommand
from courses.models import Course, Lesson


class Command(BaseCommand):
    help = 'Populate courses with educational content'

    def handle(self, *args, **options):
        self.stdout.write('Starting content population...')
        self.update_python_lessons()
        self.stdout.write(self.style.SUCCESS('Content populated successfully!'))

    def update_python_lessons(self):
        """Update Python course lessons with real content"""
        
        # Lesson 18: Установка Python
        self.update_lesson(18, """# Установка Python и настройка окружения

## Шаг 1: Скачивание Python

1. Перейдите на официальный сайт: **python.org**
2. Нажмите кнопку "Downloads"
3. Скачайте последнюю версию Python 3.x (рекомендуется 3.11 или 3.12)

## Шаг 2: Установка на Windows

1. Запустите скачанный установщик
2. **ВАЖНО**: Поставьте галочку **"Add Python to PATH"**
3. Нажмите "Install Now"
4. Дождитесь завершения установки

## Шаг 3: Проверка установки

Откройте командную строку (Win + R, введите cmd) и введите:

```bash
python --version
```

Вы должны увидеть что-то вроде: Python 3.12.0

## Шаг 4: Первые команды в Python

В командной строке введите python для запуска интерактивного режима:

```python
>>> print("Hello!")
Hello!
>>> 2 + 2
4
>>> exit()
```

## Установка Visual Studio Code

1. Скачайте с **code.visualstudio.com**
2. Установите программу
3. Откройте VS Code
4. Установите расширение "Python" от Microsoft (Ctrl+Shift+X)

Поздравляю! Вы готовы к программированию на Python!""")

        # Lesson 19: Первая программа
        self.update_lesson(19, """# Первая программа: Hello World

## Традиция Hello World

Первая программа на любом языке программирования традиционно выводит "Hello, World!" на экран.

## Создание программы

1. Откройте VS Code
2. Создайте файл hello.py
3. Введите код:

```python
print("Hello, World!")
```

4. Сохраните файл (Ctrl+S)
5. Запустите: нажмите F5 или кнопку Play

## Функция print()

print() - встроенная функция для вывода текста на экран.

```python
# Вывод текста
print("Привет, мир!")

# Вывод нескольких значений
print("Имя:", "Алексей")

# Вывод чисел
print(42)
print(3.14)

# Вывод результата вычислений
print(2 + 2)
print(10 * 5)
```

## Комментарии в коде

Комментарии - это пояснения для программистов, Python их игнорирует.

```python
# Это однострочный комментарий

print("Код выполнится")  # Комментарий в конце строки
```

## Практика

Создайте программу, которая выводит:
1. Ваше имя
2. Ваш возраст
3. Ваш любимый язык программирования""")

        # Lesson 20: Переменные и типы данных
        self.update_lesson(20, """# Переменные и типы данных

## Что такое переменная?

Переменная - это именованная область памяти для хранения данных. 

```python
# Создание переменных
name = "Алексей"     # строка
age = 25             # целое число
height = 1.75        # дробное число
is_student = True    # логическое значение
```

## Правила именования

Можно: буквы, цифры, подчёркивание, начинать с буквы
Нельзя: начинать с цифры, пробелы, зарезервированные слова

## Типы данных

### 1. Числа

```python
# int - целые числа
count = 42
year = 2024

# float - дробные числа
price = 19.99
pi = 3.14159

# Математические операции
a = 10 + 5    # 15 (сложение)
b = 10 - 5    # 5 (вычитание)
c = 10 * 5    # 50 (умножение)
d = 10 / 5    # 2.0 (деление)
e = 10 // 3   # 3 (целочисленное деление)
f = 10 % 3    # 1 (остаток)
g = 2 ** 3    # 8 (степень)
```

### 2. Строки (str)

```python
greeting = "Привет"
message = 'Мир'

# Операции
full = greeting + " " + message  # "Привет Мир"
repeated = "Ha" * 3              # "HaHaHa"

# f-строки
name = "Алексей"
age = 25
info = f"Меня зовут {name}, мне {age} лет"
```

### 3. Логический тип (bool)

```python
is_active = True
is_deleted = False

# Сравнения
print(5 > 3)   # True
print(5 == 3)  # False
```

## Ввод данных

```python
name = input("Как вас зовут? ")
print(f"Привет, {name}!")

# input всегда возвращает строку!
age_str = input("Сколько вам лет? ")
age = int(age_str)  # Преобразуем в число
```""")

        # Lesson 21: Тест по основам
        self.update_lesson(21, """# Тест: Основы Python

Проверьте свои знания!

## Вопрос 1
Какой тип данных имеет значение 3.14?
- A) int
- B) str
- C) float (правильно)
- D) bool

## Вопрос 2
Что выведет print(10 // 3)?
- A) 3.33
- B) 3 (правильно)
- C) 1
- D) 10

## Вопрос 3
Как проверить тип переменной?
- A) x.type()
- B) type(x) (правильно)
- C) typeof(x)
- D) x.typeof()

## Практические задания

### Задание 1: Калькулятор

```python
a = float(input("Первое число: "))
b = float(input("Второе число: "))

print(f"Сумма: {a + b}")
print(f"Разность: {a - b}")
print(f"Произведение: {a * b}")
print(f"Частное: {a / b}")
```

### Задание 2: Приветствие

```python
name = input("Ваше имя: ")
year = int(input("Год рождения: "))
age = 2024 - year

print(f"Привет, {name}! Тебе {age} лет.")
```

Отлично! Переходите к следующему разделу!""")

        # Lesson 22: Условные операторы
        self.update_lesson(22, """# Условные операторы if/else

## Простой if

```python
age = 18

if age >= 18:
    print("Вы совершеннолетний")
```

Важно: После if - двоеточие, код внутри - с отступом 4 пробела!

## if-else

```python
temperature = 25

if temperature > 30:
    print("Жарко!")
else:
    print("Нормальная температура")
```

## if-elif-else

```python
score = 85

if score >= 90:
    grade = "Отлично"
elif score >= 80:
    grade = "Хорошо"
elif score >= 70:
    grade = "Удовл."
else:
    grade = "Неуд."

print(f"Оценка: {grade}")
```

## Операторы сравнения

- == Равно
- != Не равно
- > Больше
- < Меньше
- >= Больше или равно
- <= Меньше или равно

## Логические операторы

```python
# and - оба условия True
if age >= 18 and has_license:
    print("Можете водить")

# or - хотя бы одно True
if day == "суббота" or day == "воскресенье":
    print("Выходной!")

# not - инвертирует
if not is_raining:
    print("Можно гулять")
```

## Тернарный оператор

```python
status = "взрослый" if age >= 18 else "ребёнок"
```

## Практика

Напишите программу-калькулятор скидок:
- Сумма > 5000 - скидка 15%
- Сумма > 2000 - скидка 10%
- Сумма > 1000 - скидка 5%""")

        # Lesson 23: Циклы
        self.update_lesson(23, """# Циклы for и while

## Цикл for

```python
# Перебор списка
fruits = ["яблоко", "банан", "апельсин"]
for fruit in fruits:
    print(fruit)

# range() - генерация чисел
for i in range(5):      # 0, 1, 2, 3, 4
    print(i)

for i in range(2, 6):   # 2, 3, 4, 5
    print(i)

for i in range(0, 10, 2): # 0, 2, 4, 6, 8
    print(i)
```

## enumerate() - индекс и значение

```python
fruits = ["яблоко", "банан"]
for i, fruit in enumerate(fruits):
    print(f"{i + 1}. {fruit}")
```

## Цикл while

```python
count = 0
while count < 5:
    print(count)
    count += 1
```

## break и continue

```python
# break - выход из цикла
for i in range(10):
    if i == 5:
        break
    print(i)  # 0, 1, 2, 3, 4

# continue - пропуск итерации
for i in range(5):
    if i == 2:
        continue
    print(i)  # 0, 1, 3, 4
```

## Примеры

### Сумма чисел

```python
total = 0
for i in range(1, 101):
    total += i
print(f"Сумма 1-100: {total}")
```

### Таблица умножения

```python
n = 7
for i in range(1, 11):
    print(f"{n} x {i} = {n * i}")
```""")

        # Lesson 24: Практика Калькулятор
        self.update_lesson(24, """# Практика: Калькулятор

## Задание

Создайте консольный калькулятор с операциями: +, -, *, /

## Решение

```python
# calculator.py

def calculator():
    print("=== КАЛЬКУЛЯТОР ===")
    print("Операции: +, -, *, /")
    print("Введите 'q' для выхода")
    
    while True:
        input1 = input("Первое число: ")
        if input1.lower() == 'q':
            print("До свидания!")
            break
        
        try:
            num1 = float(input1)
        except ValueError:
            print("Ошибка: введите число!")
            continue
        
        operation = input("Операция (+, -, *, /): ")
        if operation not in ['+', '-', '*', '/']:
            print("Неизвестная операция!")
            continue
        
        try:
            num2 = float(input("Второе число: "))
        except ValueError:
            print("Ошибка: введите число!")
            continue
        
        if operation == '+':
            result = num1 + num2
        elif operation == '-':
            result = num1 - num2
        elif operation == '*':
            result = num1 * num2
        elif operation == '/':
            if num2 == 0:
                print("Ошибка: деление на ноль!")
                continue
            result = num1 / num2
        
        print(f"Результат: {num1} {operation} {num2} = {result}")

calculator()
```

## Что вы изучили

- Ввод данных с input()
- Преобразование типов
- Условия if/elif/else
- Цикл while True с break
- Обработка ошибок try/except

## Домашнее задание

Добавьте в калькулятор:
1. Возведение в степень (**)
2. Остаток от деления (%)
3. Историю вычислений""")

        # Lesson 25: Создание функций
        self.update_lesson(25, """# Создание функций

## Что такое функция?

Функция - это блок кода, который можно вызывать многократно.

```python
# Определение функции
def greet():
    print("Привет!")

# Вызов функции
greet()  # Привет!
greet()  # Привет!
```

## Функции с параметрами

```python
def greet(name):
    print(f"Привет, {name}!")

greet("Алексей")  # Привет, Алексей!
greet("Мария")    # Привет, Мария!
```

## Параметры по умолчанию

```python
def greet(name, greeting="Привет"):
    print(f"{greeting}, {name}!")

greet("Алексей")              # Привет, Алексей!
greet("Мария", "Здравствуй")  # Здравствуй, Мария!
```

## Возврат значения

```python
def add(a, b):
    return a + b

result = add(5, 3)
print(result)  # 8
```

## Практический пример

```python
def calculate_discount(price, discount_percent=10):
    discount = price * discount_percent / 100
    return price - discount

original = 1000
final = calculate_discount(original, 20)
print(f"Цена со скидкой: {final} руб.")  # 800
```""")

        # Lesson 26: Параметры и возвращаемые значения
        self.update_lesson(26, """# Параметры и возвращаемые значения

## *args - произвольное количество аргументов

```python
def sum_all(*numbers):
    total = 0
    for num in numbers:
        total += num
    return total

print(sum_all(1, 2, 3))       # 6
print(sum_all(1, 2, 3, 4, 5)) # 15
```

## **kwargs - именованные аргументы

```python
def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

print_info(name="Алексей", age=25, city="Москва")
```

## Возврат нескольких значений

```python
def get_stats(numbers):
    minimum = min(numbers)
    maximum = max(numbers)
    average = sum(numbers) / len(numbers)
    return minimum, maximum, average

nums = [1, 2, 3, 4, 5]
min_val, max_val, avg = get_stats(nums)
print(f"Мин: {min_val}, Макс: {max_val}, Среднее: {avg}")
```

## Lambda-функции

```python
# Обычная функция
def square(x):
    return x ** 2

# Lambda-версия
square = lambda x: x ** 2

print(square(5))  # 25

# С map
numbers = [1, 2, 3, 4, 5]
squared = list(map(lambda x: x ** 2, numbers))
print(squared)  # [1, 4, 9, 16, 25]
```""")

        # Lesson 27: Импорт модулей
        self.update_lesson(27, """# Импорт модулей

## Что такое модуль?

Модуль - это файл с Python-кодом, который можно использовать в других программах.

## Встроенные модули

```python
# Импорт всего модуля
import math

print(math.pi)        # 3.141592653589793
print(math.sqrt(16))  # 4.0

# Импорт с псевдонимом
import math as m
print(m.pi)

# Импорт конкретных функций
from math import sqrt, pi
print(sqrt(25))  # 5.0
```

## Популярные модули

### random - случайные числа

```python
import random

print(random.randint(1, 100))  # Случайное целое

colors = ["red", "green", "blue"]
print(random.choice(colors))  # Случайный элемент
```

### datetime - дата и время

```python
from datetime import datetime, date

now = datetime.now()
print(now)

today = date.today()
print(today.strftime("%d.%m.%Y"))
```

### os - работа с файловой системой

```python
import os

print(os.getcwd())  # Текущая директория
print(os.listdir("."))  # Список файлов
```

### json - работа с JSON

```python
import json

data = {"name": "Алексей", "age": 25}
json_str = json.dumps(data, ensure_ascii=False)
print(json_str)
```""")

        # Lesson 28: Тест по функциям
        self.update_lesson(28, """# Тест: Функции

## Вопрос 1
Что вернёт функция без return?
- A) 0
- B) None (правильно)
- C) Ошибка
- D) Пустую строку

## Вопрос 2
Что делает *args?
- A) Обязательные аргументы
- B) Произвольное количество позиционных аргументов (правильно)
- C) Именованные аргументы
- D) Значения по умолчанию

## Вопрос 3
Как импортировать только sqrt из math?
- A) import math.sqrt
- B) from math import sqrt (правильно)
- C) import sqrt from math
- D) math.import(sqrt)

## Практические задания

### Задание 1: Факториал

```python
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(factorial(5))  # 120
```

### Задание 2: Проверка палиндрома

```python
def is_palindrome(text):
    text = text.lower().replace(" ", "")
    return text == text[::-1]

print(is_palindrome("А роза упала на лапу Азора"))  # True
```

### Задание 3: Генератор паролей

```python
import random
import string

def generate_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%"
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

print(generate_password())
```

Поздравляю! Вы освоили основы Python!""")

        self.stdout.write(self.style.SUCCESS('Python course lessons updated!'))

    def update_lesson(self, lesson_id, content):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.content = content
            lesson.save()
            self.stdout.write(f'  Updated: {lesson.title}')
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'  Lesson {lesson_id} not found'))
