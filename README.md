# 📌 Task Tracker API

## 📖 Описание

Task Tracker API — REST API на Django REST Framework для управления проектами, задачами и комментариями с JWT-аутентификацией.

Архитектура — **уровень 1: сервисный слой** (см. раздел «Архитектура» ниже).

## ⚙️ Технологии

- Python 3
- Django
- Django REST Framework
- SimpleJWT
- SQLite / PostgreSQL (Docker)
- Django Filter
- DRF Spectacular (Swagger / OpenAPI)

## 🚀 Возможности

- JWT-аутентификация
- CRUD для проектов, добавление участников
- CRUD для задач, назначение исполнителей (assignee)
- Комментарии к задачам
- Поиск, фильтрация и сортировка задач
- Swagger документация

## 📦 Установка

```bash
git clone <your-repo-url>
cd project

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

## 🧱 Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

## 👤 Создать администратора

```bash
python manage.py createsuperuser
```

## ▶️ Запуск проекта

```bash
python manage.py runserver
```

API будет доступно на http://127.0.0.1:8000/

## 🔐 JWT Авторизация

Получить токен:

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

Refresh токена: `POST /api/token/refresh/`

## 📁 API Endpoints

### 📂 Projects

```bash
# Создать проект
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test project"}'

# Список
GET /api/projects/

# Обновить (переименовать; доступно любому участнику)
PATCH /api/projects/{id}/
curl -X PATCH http://127.0.0.1:8000/api/projects/1/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"New name"}'

# Удалить (только владелец)
DELETE /api/projects/{id}/

# Добавить участника (только владелец; возвращает сериализованный проект)
POST /api/projects/{id}/add_member/
curl -X POST http://127.0.0.1:8000/api/projects/1/add_member/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 2}'
```

### 📋 Tasks

```bash
# Создать задачу
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Task 1","project":1,"status":"todo"}'

# Список (+ фильтры/поиск/сортировка)
GET /api/tasks/?project=&status=&assignee=&search=&ordering=priority

# Обновить (project менять нельзя — 400)
PATCH /api/tasks/{id}/

# Удалить (любой участник проекта)
DELETE /api/tasks/{id}/

# Комментарии задачи
GET /api/tasks/{id}/comments/
```

### 💬 Comments

```bash
curl -X POST http://127.0.0.1:8000/api/comments/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello","task":1}'
```

## 📊 Swagger / OpenAPI

- http://127.0.0.1:8000/api/schema/
- http://127.0.0.1:8000/api/schema/swagger-ui/
- http://127.0.0.1:8000/api/schema/redoc/

## 🧪 Тесты

```bash
python manage.py test
```

Юнит-тесты бизнес-логики (`test_selectors.py`, `test_services.py`) не используют `APIClient` —
вызывают функции доменного слоя напрямую. `test_api.py` проверяет только транспорт: коды
ответов, роутинг, аутентификацию.

## 🐳 Docker

```bash
docker-compose up --build
```

---

## 🏗️ Архитектура

Проект переведён на **уровень 1**: бизнес-логика собрана в сервисном и селекторном слоях,
а не размазана между `views`, `serializers` и `permissions`.

### Путь запроса

```
HTTP-запрос
    │
    ▼
View (api/views.py) — транспорт: парсинг запроса, вызов селектора/сервиса, ответ
    │
    ├──▶ Selector (selectors.py) — если это чтение: все выборки с учётом видимости
    └──▶ Service (services.py) — если это запись: бизнес-правила + изменение данных
              │
              ▼
        Model / QuerySet (models.py) — структура данных
              │
              ▼
        Serializer → Response
```

### Слои и зоны ответственности

| Слой | Файл | Отвечает за | Не имеет права |
|---|---|---|---|
| Транспорт | `tracker/api/views.py` | HTTP: парсинг запроса, вызов сервиса/селектора, код ответа | лезть в ORM, проверять бизнес-правила |
| Форма данных | `tracker/api/serializers.py` | типы полей, обязательность, choices | ходить в БД, знать про права |
| Чтение | `tracker/selectors.py` | все выборки, видимость «кто что видит» | изменять данные |
| Запись | `tracker/services.py` | бизнес-правила, создание/изменение/удаление | знать про HTTP (request, Response, DRF) |
| Данные | `tracker/models.py` | структура, простые методы о себе (`is_member`), кастомные QuerySet | сценарная логика |
| Ошибки | `tracker/exceptions.py` + `config/exception_handler.py` | доменные исключения и их перевод в HTTP-коды | — |

Стрелки импортов направлены только вниз: `views` → `serializers`, `selectors`/`services`;
`selectors`/`services` → `models`. Сервис и селектор не импортируют `rest_framework`.

### Права доступа — таблица кодов

| Ситуация | Слой | Код |
|---|---|---|
| Нет/невалиден токен | транспорт (`IsAuthenticated`) | 401 |
| Данные неправильной формы | входной сериализатор | 400 |
| Ресурс из URL не существует или невидим | селектор (`visible_to`) | 404 |
| Ресурс виден, но действие запрещено | сервис | 403 |
| Битая ссылка в теле запроса / нарушено бизнес-правило | сервис | 400 |

`permissions.py` удалён — все проверки прав живут в селекторах (видимость → 404) и сервисах
(права/бизнес-правила → 403/400).

### Структура каталогов

```
tracker/
├── models.py           # модели + кастомные QuerySet (visible_to, with_priority_order)
├── selectors.py         # все чтения
├── services.py           # все записи + бизнес-правила
├── exceptions.py         # доменные исключения
├── api/
│   ├── serializers.py    # только форма данных
│   ├── views.py          # тонкий транспорт
│   └── urls.py
├── admin.py
├── migrations/
└── tests/
    ├── test_selectors.py # юнит-тесты чтения, без HTTP
    ├── test_services.py  # юнит-тесты бизнес-правил, без HTTP
    └── test_api.py        # тесты транспорта: коды, роутинг, контракт
config/
├── exception_handler.py  # доменные исключения → HTTP-коды
└── ...
```

### Про сервисный слой vs «Django-way»

Django и DRF не навязывают архитектуру выше MTV — сервисный слой это соглашение поверх
фреймворка. У подхода есть известная критика (Джеймс Беннетт, «Against service layers in
Django»): для простого CRUD без прав слой — лишняя церемония, логике место в моделях и
менеджерах. Для этого трекера — с правами на каждое действие и перспективой второго
транспорта (бот, management-команда) — слой окупается: одно и то же правило не приходится
искать по трём файлам и вспоминать в каждой новой точке входа.
"# Niyazov09-task-tracker_v2" 
"# Niyazov09-task-tracker_v2" 
