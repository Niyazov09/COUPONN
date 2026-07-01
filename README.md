📌 Task Tracker API
📖 Описание

Task Tracker API — REST API на Django REST Framework для управления проектами, задачами и комментариями с JWT-аутентификацией.

⚙️ Технологии
Python 3
Django
Django REST Framework
SimpleJWT
SQLite / PostgreSQL (Docker)
Django Filter
DRF Spectacular (Swagger / OpenAPI)
🚀 Возможности
JWT-аутентификация
CRUD для проектов
Добавление участников в проекты
CRUD для задач
Назначение исполнителей (assignee)
Комментарии к задачам
Поиск задач
Фильтрация и сортировка
Swagger документация
📦 Установка
1. Клонировать проект
git clone <your-repo-url>
cd project
2. Виртуальное окружение
python -m venv venv
Windows:
venv\Scripts\activate
3. Установить зависимости
pip install -r requirements.txt
🧱 Миграции
python manage.py makemigrations
python manage.py migrate
👤 Создать администратора
python manage.py createsuperuser
▶️ Запуск проекта
python manage.py runserver

API будет доступно:

http://127.0.0.1:8000/
🔐 JWT Авторизация
Получить токен
curl -X POST http://127.0.0.1:8000/api/token/ ^
-H "Content-Type: application/json" ^
-d "{\"username\":\"admin\",\"password\":\"admin123\"}"
Refresh токена
POST /api/token/refresh/
📁 API Endpoints
📂 Projects
Создать проект
curl -X POST http://127.0.0.1:8000/api/projects/ ^
-H "Authorization: Bearer <token>" ^
-H "Content-Type: application/json" ^
-d "{\"name\":\"Test project\"}"
Получить список
GET /api/projects/
Обновить
PATCH /api/projects/{id}/
Удалить
DELETE /api/projects/{id}/
Добавить участника
POST /api/projects/{id}/add_member/
📋 Tasks
Создать задачу
curl -X POST http://127.0.0.1:8000/api/tasks/ ^
-H "Authorization: Bearer <token>" ^
-H "Content-Type: application/json" ^
-d "{\"title\":\"Task 1\",\"project\":1,\"status\":\"todo\"}"
Получить список
GET /api/tasks/
Обновить
PATCH /api/tasks/{id}/
Удалить
DELETE /api/tasks/{id}/
Комментарии задачи
GET /api/tasks/{id}/comments/
💬 Comments
Создать комментарий
curl -X POST http://127.0.0.1:8000/api/comments/ ^
-H "Authorization: Bearer <token>" ^
-H "Content-Type: application/json" ^
-d "{\"text\":\"Hello\",\"task\":1}"
📊 Swagger / OpenAPI
http://127.0.0.1:8000/api/schema/
http://127.0.0.1:8000/api/schema/swagger-ui/
http://127.0.0.1:8000/api/schema/redoc/
🧪 Тесты
python manage.py test
🐳 Docker (если используешь)
docker-compose up --build
👨‍💻 Автор

Shokhzhakhon
Учебный проект Django REST Framework