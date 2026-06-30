📌 Task Tracker API
📖 Описание

Task Tracker API — REST API на Django REST Framework для управления проектами, задачами и комментариями с JWT-аутентификацией.

⚙️ Технологии
Python 3
Django
Django REST Framework
SimpleJWT
SQLite
Django Filter
DRF Spectacular (Swagger / OpenAPI)
🚀 Возможности
JWT-аутентификация
Создание проектов
Добавление участников в проекты
Создание задач
Назначение исполнителей (assignee)
Комментарии к задачам
Поиск задач
Фильтрация и сортировка
Swagger документация
📦 Установка
1. Создать виртуальное окружение
python -m venv venv
2. Активировать

Windows:
venv\Scripts\activate

3. Установить зависимости
pip install django
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install django-filter
pip install drf-spectacular
🧱 Миграции
python manage.py makemigrations
python manage.py migrate
👤 Создать администратора
python manage.py createsuperuser
▶️ Запуск
python manage.py runserver
API будет доступно:
http://127.0.0.1:8000/
🔐 JWT Авторизация
Получить токен:
POST /api/token/
Обновить токен:
POST /api/token/refresh/
📁 API Endpoints
📂 Projects
GET    /api/projects/
POST   /api/projects/
PATCH  /api/projects/{id}/
DELETE /api/projects/{id}/
POST   /api/projects/{id}/add_member/
📋 Tasks
GET    /api/tasks/
POST   /api/tasks/
PATCH  /api/tasks/{id}/
DELETE /api/tasks/{id}/
GET    /api/tasks/{id}/comments/
💬 Comments
GET    /api/comments/
POST   /api/comments/
PATCH  /api/comments/{id}/
DELETE /api/comments/{id}/
📊 Swagger / OpenAPI
Schema:
/api/schema/
Swagger UI:
/api/schema/swagger-ui/
/api/schema/redoc/
🧪 Тесты
python manage.py test
👨‍💻 Автор:shokhzhakhon
Учебный проект Django REST Framework