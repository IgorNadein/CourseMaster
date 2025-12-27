from django.core.management.base import BaseCommand
from courses.models import Lesson


class Command(BaseCommand):
    help = 'Populate JavaScript course with content'

    def handle(self, *args, **options):
        self.stdout.write('Updating JavaScript course...')
        
        # Lesson 29: Введение в JavaScript
        self.update_lesson(29, """# Введение в JavaScript

![JavaScript Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Unofficial_JavaScript_logo_2.svg/200px-Unofficial_JavaScript_logo_2.svg.png)

## Что такое JavaScript?

JavaScript (JS) - это язык программирования для веб-разработки. Он позволяет:

- Делать веб-страницы интерактивными
- Обрабатывать действия пользователя (клики, ввод)
- Изменять содержимое страницы
- Общаться с сервером (AJAX, fetch)
- Создавать полноценные приложения

## Где используется JavaScript?

### Frontend (браузер)
- React, Vue, Angular
- Интерактивные элементы
- Анимации

### Backend (сервер)
- Node.js
- Express, Nest.js
- API серверы

### Мобильные приложения
- React Native
- Ionic

### Десктоп
- Electron (VS Code, Slack)

## Подключение к HTML

### Способ 1: Внутри HTML

```html
<!DOCTYPE html>
<html>
<head>
    <title>JS Demo</title>
</head>
<body>
    <h1>Hello</h1>
    
    <script>
        console.log("Hello from JavaScript!");
        alert("Привет!");
    </script>
</body>
</html>
```

### Способ 2: Внешний файл (рекомендуется)

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
<head>
    <title>JS Demo</title>
</head>
<body>
    <h1>Hello</h1>
    
    <script src="script.js"></script>
</body>
</html>
```

```javascript
// script.js
console.log("Hello from external file!");
```

## Консоль разработчика

Откройте DevTools: F12 или Ctrl+Shift+I

Вкладка Console - здесь можно:
- Видеть вывод console.log()
- Писать и выполнять JS код
- Отлаживать ошибки

## Первая программа

```javascript
// Вывод в консоль
console.log("Hello, World!");

// Вывод в alert
alert("Привет!");

// Вывод на страницу
document.write("<h2>Hello</h2>");
```

## Комментарии

```javascript
// Однострочный комментарий

/*
   Многострочный
   комментарий
*/
```

Начнём изучать переменные!""")

        # Lesson 30: Переменные
        self.update_lesson(30, """# Переменные: let, const, var

## Объявление переменных

В JavaScript есть три способа объявить переменную:

### let - изменяемая переменная

```javascript
let name = "Алексей";
let age = 25;

// Можно изменить
name = "Мария";
age = 30;
```

### const - константа

```javascript
const PI = 3.14159;
const API_URL = "https://api.example.com";

// НЕЛЬЗЯ изменить!
PI = 3.14; // Ошибка!
```

Используйте const по умолчанию, let когда нужно изменять.

### var - устаревший способ

```javascript
var oldStyle = "Не рекомендуется";
```

Имеет проблемы с областью видимости. Не используйте в новом коде.

## Правила именования

```javascript
// Хорошо (camelCase)
let userName = "Алексей";
let isActive = true;
let itemCount = 42;

// Константы БОЛЬШИМИ_БУКВАМИ
const MAX_SIZE = 100;
const API_KEY = "abc123";

// Плохо
let user-name = "error";  // Дефис
let 2users = 10;          // Начинается с цифры
let class = "reserved";   // Зарезервированное слово
```

## Область видимости

```javascript
// Глобальная
let globalVar = "Видна везде";

function example() {
    // Локальная
    let localVar = "Видна только в функции";
    
    if (true) {
        // Блочная
        let blockVar = "Видна только в блоке";
        console.log(blockVar); // OK
    }
    // console.log(blockVar); // Ошибка!
}
```

## Hoisting (подъём)

```javascript
// var поднимается
console.log(x); // undefined (не ошибка!)
var x = 5;

// let/const не поднимаются
console.log(y); // Ошибка!
let y = 5;
```

## Практика

```javascript
// Создайте переменные для:
const firstName = "Алексей";
const lastName = "Петров";
let age = 25;
const isStudent = true;

// Выведите информацию
console.log(`${firstName} ${lastName}, ${age} лет`);
```""")

        # Lesson 31: Типы данных
        self.update_lesson(31, """# Типы данных

## Примитивные типы

### String (строка)

```javascript
let name = "Алексей";
let greeting = 'Привет';
let message = `Привет, ${name}!`;  // Шаблонная строка

// Методы
console.log(name.length);        // 7
console.log(name.toUpperCase()); // "АЛЕКСЕЙ"
console.log(name.toLowerCase()); // "алексей"
console.log(name.slice(0, 3));   // "Але"
console.log(name.includes("е")); // true
```

### Number (число)

```javascript
let integer = 42;
let float = 3.14;
let negative = -10;

// Операции
let sum = 10 + 5;     // 15
let diff = 10 - 5;    // 5
let product = 10 * 5; // 50
let quotient = 10 / 3; // 3.333...
let remainder = 10 % 3; // 1
let power = 2 ** 3;   // 8

// Специальные значения
let inf = Infinity;
let notNum = NaN; // Not a Number
```

### Boolean (логический)

```javascript
let isActive = true;
let isDeleted = false;

// Сравнения
console.log(5 > 3);   // true
console.log(5 === 5); // true (строгое равенство)
console.log(5 == "5"); // true (нестрогое)
console.log(5 === "5"); // false (разные типы)
```

### null и undefined

```javascript
let empty = null;        // Явно пустое значение
let notDefined;          // undefined (не определено)

console.log(typeof null);      // "object" (баг в JS)
console.log(typeof undefined); // "undefined"
```

## Сложные типы

### Array (массив)

```javascript
let fruits = ["яблоко", "банан", "апельсин"];

console.log(fruits[0]);      // "яблоко"
console.log(fruits.length);  // 3

fruits.push("груша");        // Добавить в конец
fruits.pop();                // Удалить последний
fruits.shift();              // Удалить первый
fruits.unshift("киви");      // Добавить в начало
```

### Object (объект)

```javascript
let person = {
    name: "Алексей",
    age: 25,
    isStudent: true,
    skills: ["JS", "Python"]
};

console.log(person.name);     // "Алексей"
console.log(person["age"]);   // 25
person.city = "Москва";       // Добавить свойство
delete person.isStudent;      // Удалить свойство
```

## typeof

```javascript
console.log(typeof "hello");    // "string"
console.log(typeof 42);         // "number"
console.log(typeof true);       // "boolean"
console.log(typeof undefined);  // "undefined"
console.log(typeof {});         // "object"
console.log(typeof []);         // "object" (массив тоже объект)
console.log(typeof null);       // "object" (известный баг)
```

## Преобразование типов

```javascript
// В строку
String(123);      // "123"
(123).toString(); // "123"

// В число
Number("42");     // 42
parseInt("42px"); // 42
parseFloat("3.14"); // 3.14

// В boolean
Boolean(1);       // true
Boolean(0);       // false
Boolean("");      // false
Boolean("text");  // true
```""")

        # Lesson 32: Что такое DOM
        self.update_lesson(32, """# Что такое DOM

## DOM - Document Object Model

DOM - это представление HTML-документа в виде дерева объектов, которыми можно управлять с помощью JavaScript.

```
document
  └── html
       ├── head
       │    └── title
       └── body
            ├── h1
            ├── div
            │    ├── p
            │    └── p
            └── footer
```

![DOM Tree](https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&h=300)

## Объект document

```javascript
// Доступ к документу
console.log(document);

// Заголовок страницы
console.log(document.title);
document.title = "Новый заголовок";

// URL страницы
console.log(document.URL);

// Все ссылки
console.log(document.links);

// Все формы
console.log(document.forms);
```

## Типы узлов

- **Element** - HTML-элемент (div, p, h1)
- **Text** - текстовое содержимое
- **Document** - весь документ
- **Comment** - HTML-комментарий

## Отношения между узлами

```javascript
let element = document.querySelector('div');

// Родитель
element.parentNode;
element.parentElement;

// Дети
element.childNodes;      // Все узлы (включая текст)
element.children;        // Только элементы
element.firstChild;
element.lastChild;

// Соседи
element.nextSibling;
element.previousSibling;
element.nextElementSibling;
element.previousElementSibling;
```

## Пример структуры

```html
<div id="container">
    <h1>Заголовок</h1>
    <p class="intro">Первый параграф</p>
    <p>Второй параграф</p>
</div>
```

```javascript
let container = document.getElementById('container');

console.log(container.children.length); // 3
console.log(container.firstElementChild.textContent); // "Заголовок"
console.log(container.lastElementChild.textContent);  // "Второй параграф"
```

## Зачем нужен DOM?

1. Изменять содержимое страницы
2. Добавлять/удалять элементы
3. Менять стили
4. Реагировать на действия пользователя
5. Создавать интерактивные интерфейсы

В следующем уроке научимся выбирать элементы!""")

        # Lesson 33: Выбор элементов
        self.update_lesson(33, """# Выбор элементов

## Методы выбора

### getElementById

Выбирает элемент по id (возвращает один элемент):

```javascript
let header = document.getElementById('header');
console.log(header);
```

### querySelector

Выбирает первый элемент по CSS-селектору:

```javascript
// По тегу
let div = document.querySelector('div');

// По классу
let intro = document.querySelector('.intro');

// По id
let header = document.querySelector('#header');

// Сложный селектор
let link = document.querySelector('nav a.active');
```

### querySelectorAll

Выбирает все элементы по селектору (возвращает NodeList):

```javascript
let paragraphs = document.querySelectorAll('p');

// Перебор
paragraphs.forEach(p => {
    console.log(p.textContent);
});

// Или через индекс
console.log(paragraphs[0]);
console.log(paragraphs.length);
```

### getElementsByClassName

```javascript
let items = document.getElementsByClassName('item');
// Возвращает HTMLCollection (живая коллекция)
```

### getElementsByTagName

```javascript
let divs = document.getElementsByTagName('div');
```

## Сравнение методов

| Метод | Возвращает | Селектор |
|-------|-----------|----------|
| getElementById | Element | id |
| querySelector | Element | CSS |
| querySelectorAll | NodeList | CSS |
| getElementsByClassName | HTMLCollection | class |
| getElementsByTagName | HTMLCollection | tag |

## Практические примеры

```html
<div id="app">
    <h1 class="title">Заголовок</h1>
    <ul class="list">
        <li class="item">Первый</li>
        <li class="item">Второй</li>
        <li class="item active">Третий</li>
    </ul>
    <button id="btn">Нажми</button>
</div>
```

```javascript
// Выбор элементов
let app = document.getElementById('app');
let title = document.querySelector('.title');
let items = document.querySelectorAll('.item');
let activeItem = document.querySelector('.item.active');
let button = document.querySelector('#btn');

// Работа с элементами
console.log(title.textContent);  // "Заголовок"
console.log(items.length);       // 3
console.log(activeItem.textContent); // "Третий"
```

## Проверка существования

```javascript
let element = document.querySelector('.maybe-exists');

if (element) {
    console.log("Элемент найден!");
} else {
    console.log("Элемент не найден");
}
```""")

        # Lesson 34: Изменение элементов
        self.update_lesson(34, """# Изменение элементов

## Изменение содержимого

### textContent

```javascript
let title = document.querySelector('h1');

// Получить текст
console.log(title.textContent);

// Изменить текст
title.textContent = "Новый заголовок";
```

### innerHTML

```javascript
let container = document.querySelector('.container');

// Получить HTML
console.log(container.innerHTML);

// Изменить HTML
container.innerHTML = "<p>Новый <strong>параграф</strong></p>";

// Добавить HTML
container.innerHTML += "<p>Ещё один</p>";
```

## Изменение стилей

### style

```javascript
let box = document.querySelector('.box');

box.style.color = "red";
box.style.backgroundColor = "yellow";  // camelCase!
box.style.fontSize = "20px";
box.style.border = "2px solid black";
```

### classList

```javascript
let element = document.querySelector('.item');

// Добавить класс
element.classList.add('active');

// Удалить класс
element.classList.remove('hidden');

// Переключить (toggle)
element.classList.toggle('selected');

// Проверить наличие
if (element.classList.contains('active')) {
    console.log("Активен!");
}
```

## Изменение атрибутов

```javascript
let link = document.querySelector('a');
let img = document.querySelector('img');

// Получить атрибут
console.log(link.getAttribute('href'));

// Установить атрибут
link.setAttribute('href', 'https://google.com');
link.setAttribute('target', '_blank');

// Удалить атрибут
link.removeAttribute('target');

// Проверить наличие
if (link.hasAttribute('href')) {
    console.log("Есть href");
}

// Или напрямую для стандартных атрибутов
img.src = "new-image.jpg";
img.alt = "Описание";
link.href = "https://example.com";
```

## Создание элементов

```javascript
// Создать элемент
let newDiv = document.createElement('div');
newDiv.textContent = "Новый блок";
newDiv.classList.add('box');

// Добавить в DOM
let container = document.querySelector('.container');
container.appendChild(newDiv);

// Добавить в начало
container.prepend(newDiv);

// Вставить перед элементом
let ref = document.querySelector('.ref');
container.insertBefore(newDiv, ref);
```

## Удаление элементов

```javascript
let element = document.querySelector('.to-delete');

// Удалить
element.remove();

// Или через родителя
element.parentNode.removeChild(element);
```

## Практический пример

```javascript
// Создание карточки товара
function createProductCard(name, price) {
    let card = document.createElement('div');
    card.classList.add('product-card');
    
    card.innerHTML = `
        <h3>${name}</h3>
        <p class="price">${price} руб.</p>
        <button>Купить</button>
    `;
    
    return card;
}

let container = document.querySelector('.products');
container.appendChild(createProductCard("iPhone", 99990));
container.appendChild(createProductCard("MacBook", 149990));
```""")

        # Lesson 35: Практика Todo List
        self.update_lesson(35, """# Практика: Todo List

![Todo App Demo](https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif)

## Задание

Создадим простое приложение для управления списком задач.

## HTML

```html
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Todo List</title>
    <style>
        body { font-family: Arial; max-width: 500px; margin: 50px auto; }
        .todo-item { display: flex; align-items: center; padding: 10px; border-bottom: 1px solid #eee; }
        .todo-item.completed span { text-decoration: line-through; color: #888; }
        .todo-item span { flex: 1; }
        input[type="text"] { padding: 10px; width: 70%; }
        button { padding: 10px 20px; cursor: pointer; }
        .delete-btn { background: #ff4444; color: white; border: none; border-radius: 4px; }
    </style>
</head>
<body>
    <h1>Todo List</h1>
    
    <div class="add-form">
        <input type="text" id="taskInput" placeholder="Новая задача...">
        <button id="addBtn">Добавить</button>
    </div>
    
    <div id="todoList"></div>
    
    <script src="todo.js"></script>
</body>
</html>
```

## JavaScript

```javascript
// todo.js

// Элементы DOM
const taskInput = document.getElementById('taskInput');
const addBtn = document.getElementById('addBtn');
const todoList = document.getElementById('todoList');

// Массив задач
let tasks = [];

// Функция рендера списка
function renderTasks() {
    todoList.innerHTML = '';
    
    tasks.forEach((task, index) => {
        const div = document.createElement('div');
        div.classList.add('todo-item');
        if (task.completed) {
            div.classList.add('completed');
        }
        
        div.innerHTML = `
            <input type="checkbox" ${task.completed ? 'checked' : ''}>
            <span>${task.text}</span>
            <button class="delete-btn">Удалить</button>
        `;
        
        // Обработчик чекбокса
        const checkbox = div.querySelector('input');
        checkbox.addEventListener('change', () => {
            tasks[index].completed = checkbox.checked;
            renderTasks();
        });
        
        // Обработчик удаления
        const deleteBtn = div.querySelector('.delete-btn');
        deleteBtn.addEventListener('click', () => {
            tasks.splice(index, 1);
            renderTasks();
        });
        
        todoList.appendChild(div);
    });
}

// Добавление задачи
function addTask() {
    const text = taskInput.value.trim();
    
    if (text === '') {
        alert('Введите текст задачи!');
        return;
    }
    
    tasks.push({
        text: text,
        completed: false
    });
    
    taskInput.value = '';
    renderTasks();
}

// Обработчики событий
addBtn.addEventListener('click', addTask);

taskInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addTask();
    }
});

// Начальный рендер
renderTasks();
```

## Что вы изучили

1. Выбор элементов DOM
2. Создание элементов
3. Обработка событий (click, keypress, change)
4. Работа с массивами
5. Динамический рендеринг

## Домашнее задание

Добавьте:
1. Сохранение в localStorage
2. Фильтрацию (все/активные/завершённые)
3. Редактирование задач
4. Счётчик задач

Поздравляю! Вы освоили основы JavaScript и DOM!""")

        self.stdout.write(self.style.SUCCESS('JavaScript course updated!'))

    def update_lesson(self, lesson_id, content):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.content = content
            lesson.save()
            self.stdout.write(f'  Updated: {lesson.title}')
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'  Lesson {lesson_id} not found'))
