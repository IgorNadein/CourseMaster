from django.core.management.base import BaseCommand
from courses.models import Lesson


class Command(BaseCommand):
    help = 'Populate Git course with content'

    def handle(self, *args, **options):
        self.stdout.write('Updating Git course...')
        
        # Lesson 58: Что такое Git
        self.update_lesson(58, """# Что такое Git и зачем он нужен

![Git Logo](https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Git-logo.svg/200px-Git-logo.svg.png)

## Проблема без Git

Представьте: вы работаете над проектом и сохраняете файлы так:
- project_v1.zip
- project_v2.zip
- project_final.zip
- project_final_v2.zip
- project_REALLY_final.zip

Знакомо? Git решает эту проблему!

## Что такое Git?

Git - это система контроля версий (VCS). Она позволяет:

- Сохранять историю всех изменений
- Возвращаться к любой версии
- Работать в команде над одним проектом
- Создавать ветки для экспериментов
- Объединять изменения от разных разработчиков

## Основные понятия

### Репозиторий (Repository)
Папка проекта, в которой Git отслеживает все изменения.

### Коммит (Commit)
"Снимок" состояния проекта в определённый момент времени.

### Ветка (Branch)
Независимая линия разработки. Позволяет работать над фичей, не ломая основной код.

## Почему именно Git?

1. **Распределённость** - каждый разработчик имеет полную копию репозитория
2. **Скорость** - большинство операций выполняются локально
3. **Популярность** - используется в 90%+ проектов
4. **GitHub/GitLab** - удобные платформы для хостинга

## Git vs GitHub

- **Git** - программа для контроля версий (устанавливается на компьютер)
- **GitHub** - веб-платформа для хранения репозиториев в облаке

## Кто использует Git?

- Google, Microsoft, Apple
- Netflix, Spotify, Airbnb
- Все современные IT-компании
- Open Source проекты (Linux, React, Django)

В следующем уроке установим Git!""")

        # Lesson 59: Установка Git
        self.update_lesson(59, """# Установка Git

## Установка на Windows

### Шаг 1: Скачивание

1. Перейдите на git-scm.com
2. Нажмите "Download for Windows"
3. Скачайте установщик

### Шаг 2: Установка

1. Запустите установщик
2. Нажимайте "Next" (настройки по умолчанию подходят)
3. Важно: выберите "Git Bash Here" в контекстном меню
4. Завершите установку

### Шаг 3: Проверка

Откройте командную строку и введите:

```bash
git --version
```

Вы увидите: git version 2.43.0 (или новее)

## Первоначальная настройка

Укажите ваше имя и email (они будут в каждом коммите):

```bash
git config --global user.name "Ваше Имя"
git config --global user.email "your@email.com"
```

Проверка настроек:

```bash
git config --list
```

## Настройка редактора

По умолчанию Git использует Vim. Можно изменить на VS Code:

```bash
git config --global core.editor "code --wait"
```

## Git Bash

Git Bash - это терминал для Windows с командами Linux. Рекомендую использовать его:

- Правый клик в папке -> "Git Bash Here"
- Или найдите "Git Bash" в меню Пуск

## Полезные команды терминала

```bash
pwd     # Текущая директория
ls      # Список файлов
cd      # Перейти в папку
mkdir   # Создать папку
touch   # Создать файл
clear   # Очистить экран
```

Готово! Теперь создадим первый репозиторий!""")

        # Lesson 60: Первый репозиторий
        self.update_lesson(60, """# Первый репозиторий

## Создание репозитория

### Шаг 1: Создайте папку проекта

```bash
mkdir my-first-repo
cd my-first-repo
```

### Шаг 2: Инициализация Git

```bash
git init
```

Появится сообщение: Initialized empty Git repository

Теперь в папке есть скрытая папка .git - это и есть репозиторий!

## Первый коммит

### Шаг 1: Создайте файл

```bash
echo "# Мой первый проект" > README.md
```

### Шаг 2: Проверьте статус

```bash
git status
```

Вы увидите "Untracked files: README.md"

### Шаг 3: Добавьте файл в индекс

```bash
git add README.md
```

Или добавить все файлы:

```bash
git add .
```

### Шаг 4: Создайте коммит

```bash
git commit -m "Первый коммит: добавлен README"
```

## Просмотр истории

```bash
git log
```

Покажет историю коммитов с хешами, авторами и датами.

Краткий вариант:

```bash
git log --oneline
```

## Основные команды

| Команда | Описание |
|---------|----------|
| git init | Создать репозиторий |
| git status | Проверить статус |
| git add | Добавить в индекс |
| git commit -m | Создать коммит |
| git log | История коммитов |
| git diff | Показать изменения |

## .gitignore

Файл для исключения файлов из отслеживания:

```
# .gitignore
node_modules/
.env
*.log
__pycache__/
.venv/
```

## Практика

1. Создайте репозиторий
2. Добавьте файл index.html
3. Сделайте коммит
4. Измените файл
5. Сделайте ещё один коммит
6. Посмотрите историю""")

        # Lesson 61: Тест Git
        self.update_lesson(61, """# Тест: Основы Git

## Вопрос 1
Какая команда создаёт новый репозиторий?
- A) git create
- B) git new
- C) git init (правильно)
- D) git start

## Вопрос 2
Что делает git add?
- A) Создаёт коммит
- B) Добавляет файлы в индекс (правильно)
- C) Отправляет на GitHub
- D) Скачивает репозиторий

## Вопрос 3
Как посмотреть историю коммитов?
- A) git history
- B) git log (правильно)
- C) git commits
- D) git show

## Практические задания

### Задание 1: Создание репозитория

```bash
mkdir test-project
cd test-project
git init
echo "Hello Git" > hello.txt
git add hello.txt
git commit -m "Add hello.txt"
git log
```

### Задание 2: Несколько коммитов

```bash
echo "Line 2" >> hello.txt
git add .
git commit -m "Add line 2"

echo "Line 3" >> hello.txt
git commit -am "Add line 3"

git log --oneline
```

### Задание 3: .gitignore

Создайте файл .gitignore:
```
*.log
temp/
.env
```

Отлично! Переходите к работе с GitHub!""")

        # Lesson 62: Регистрация на GitHub
        self.update_lesson(62, """# Регистрация на GitHub

## Что такое GitHub?

GitHub - это платформа для хостинга Git-репозиториев в облаке. Позволяет:

- Хранить код в интернете
- Делиться проектами
- Работать в команде
- Делать code review
- Автоматизировать сборку (CI/CD)

## Создание аккаунта

### Шаг 1: Регистрация

1. Перейдите на github.com
2. Нажмите "Sign up"
3. Введите email, пароль, username
4. Пройдите капчу
5. Подтвердите email

### Шаг 2: Настройка профиля

1. Добавьте фото
2. Укажите имя
3. Напишите краткое bio

## Создание репозитория на GitHub

1. Нажмите "+" в правом верхнем углу
2. "New repository"
3. Введите название (например: my-first-repo)
4. Добавьте описание
5. Выберите Public или Private
6. Нажмите "Create repository"

## Связь локального репозитория с GitHub

### Способ 1: Для нового репозитория

```bash
git remote add origin https://github.com/username/repo.git
git branch -M main
git push -u origin main
```

### Способ 2: Клонирование существующего

```bash
git clone https://github.com/username/repo.git
cd repo
```

## SSH ключи (рекомендуется)

Для работы без ввода пароля каждый раз:

```bash
# Генерация ключа
ssh-keygen -t ed25519 -C "your@email.com"

# Копирование ключа
cat ~/.ssh/id_ed25519.pub
```

Добавьте ключ в Settings -> SSH and GPG keys на GitHub.

## Практика

1. Создайте аккаунт на GitHub
2. Создайте репозиторий
3. Свяжите его с локальным
4. Сделайте push""")

        # Lesson 63: Push и Pull
        self.update_lesson(63, """# Push и Pull

## git push - отправка изменений

Отправляет ваши коммиты на удалённый сервер (GitHub):

```bash
git push origin main
```

После первого push с флагом -u можно просто:

```bash
git push
```

## git pull - получение изменений

Скачивает изменения с сервера и объединяет с вашими:

```bash
git pull origin main
```

Или просто:

```bash
git pull
```

## git fetch - только скачать

Скачивает изменения, но НЕ объединяет:

```bash
git fetch
```

Полезно, чтобы сначала посмотреть изменения.

## Типичный рабочий процесс

```bash
# 1. Перед началом работы - получить изменения
git pull

# 2. Работаем над кодом
# ... редактируем файлы ...

# 3. Добавляем и коммитим
git add .
git commit -m "Описание изменений"

# 4. Отправляем на сервер
git push
```

## Конфликты

Если вы и коллега изменили один файл:

```bash
git pull
# CONFLICT in file.txt

# Откройте файл, решите конфликт
# Удалите маркеры <<<<< ===== >>>>>

git add file.txt
git commit -m "Resolve conflict"
git push
```

## git remote

Управление удалёнными репозиториями:

```bash
# Список удалённых
git remote -v

# Добавить удалённый
git remote add origin URL

# Удалить
git remote remove origin

# Изменить URL
git remote set-url origin NEW_URL
```

## Практика

1. Сделайте изменение локально
2. Закоммитьте
3. Сделайте push
4. Проверьте на GitHub
5. Измените файл на GitHub
6. Сделайте pull""")

        # Lesson 64: Pull Requests
        self.update_lesson(64, """# Pull Requests

## Что такое Pull Request?

Pull Request (PR) - это запрос на слияние изменений из одной ветки в другую. Основной инструмент для:

- Code review
- Обсуждения изменений
- Проверки кода перед слиянием
- Командной работы

## Создание ветки

```bash
# Создать и переключиться на ветку
git checkout -b feature/new-button

# Или отдельно
git branch feature/new-button
git checkout feature/new-button
```

## Работа в ветке

```bash
# Делаем изменения
echo "New feature" >> feature.txt
git add .
git commit -m "Add new feature"

# Отправляем ветку на GitHub
git push -u origin feature/new-button
```

## Создание Pull Request на GitHub

1. Перейдите в репозиторий на GitHub
2. Нажмите "Compare & pull request" (появится после push)
3. Или: Pull requests -> New pull request
4. Выберите ветки (base: main, compare: feature/new-button)
5. Добавьте заголовок и описание
6. Нажмите "Create pull request"

## Code Review

В PR можно:
- Оставлять комментарии к коду
- Запрашивать изменения
- Одобрять (Approve)
- Обсуждать в общем чате

## Слияние PR

После одобрения:
1. Нажмите "Merge pull request"
2. Выберите тип слияния:
   - Merge commit
   - Squash and merge
   - Rebase and merge
3. Подтвердите слияние
4. Удалите ветку (опционально)

## После слияния

```bash
# Переключиться на main
git checkout main

# Получить изменения
git pull

# Удалить локальную ветку
git branch -d feature/new-button
```

## Best Practices

1. Маленькие PR легче ревьюить
2. Описывайте что и зачем изменили
3. Добавляйте скриншоты для UI-изменений
4. Отвечайте на комментарии
5. Не пушьте в main напрямую

Поздравляю! Вы освоили основы Git и GitHub!""")

        self.stdout.write(self.style.SUCCESS('Git course updated!'))

    def update_lesson(self, lesson_id, content):
        try:
            lesson = Lesson.objects.get(id=lesson_id)
            lesson.content = content
            lesson.save()
            self.stdout.write(f'  Updated: {lesson.title}')
        except Lesson.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'  Lesson {lesson_id} not found'))
