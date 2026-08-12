"""Все записи и бизнес-правила домена.

Контракт: keyword-only аргументы, type hints. Первый аргумент — actor
(кто совершает действие), не request. На входе — простые данные (id,
строки), объекты сервис достаёт сам. Порядок проверок: существование
данных из запроса -> права actor'а -> бизнес-валидация -> запись.
Ошибки — только доменные исключения. Не импортирует DRF/HTTP-слой.
"""
from django.contrib.auth.models import User

from . import selectors
from .exceptions import BusinessValidationError, PermissionDeniedError
from .models import Comment, Project, Task

TASK_WRITABLE_FIELDS = ("title", "description", "status", "priority", "assignee")


# ---------------- PROJECT ----------------

def project_create(*, owner: User, name: str) -> Project:
    return Project.objects.create(owner=owner, name=name)


def project_update(*, actor: User, project_id: int, name: str) -> Project:
    project = selectors.project_get(user=actor, project_id=project_id)
    project.name = name
    project.save(update_fields=["name"])
    return project


def project_delete(*, actor: User, project_id: int) -> None:
    project = selectors.project_get(user=actor, project_id=project_id)

    if project.owner != actor:
        raise PermissionDeniedError(
            "Только владелец проекта может его удалить."
        )

    project.delete()


def project_add_member(*, actor: User, project_id: int, user_id: int) -> Project:
    project = selectors.project_get(user=actor, project_id=project_id)

    if project.owner != actor:
        raise PermissionDeniedError(
            "Только владелец проекта может добавлять участников."
        )

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise BusinessValidationError({"user_id": ["Пользователь не найден."]})

    if project.members.filter(id=user.id).exists():
        return project

    project.members.add(user)
    return project


# ---------------- TASK ----------------

def task_create(
    *,
    actor: User,
    project_id: int,
    title: str,
    description: str = "",
    status: str = "todo",
    priority: str = "medium",
    assignee_id: int | None = None,
) -> Task:
    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        raise BusinessValidationError({"project": ["Проект не найден."]})

    if not project.is_member(actor):
        raise PermissionDeniedError("Вы не являетесь участником проекта.")

    assignee = _resolve_assignee(project, assignee_id)

    return Task.objects.create(
        project=project,
        title=title,
        description=description,
        status=status,
        priority=priority,
        assignee=assignee,
    )


def task_update(*, actor: User, task_id: int, data: dict) -> Task:
    task = selectors.task_get(user=actor, task_id=task_id)

    if "project" in data:
        raise BusinessValidationError({"project": ["Менять проект задачи нельзя."]})

    if "assignee" in data and data["assignee"] is not None:
        data["assignee"] = _resolve_assignee(task.project, data["assignee"])

    update_fields = []
    for field in TASK_WRITABLE_FIELDS:
        if field in data:
            setattr(task, field, data[field])
            update_fields.append(field)

    if update_fields:
        task.save(update_fields=update_fields)

    return task


def task_delete(*, actor: User, task_id: int) -> None:
    selectors.task_get(user=actor, task_id=task_id).delete()


def _resolve_assignee(project: Project, assignee_id: int | None) -> User | None:
    if assignee_id is None:
        return None

    try:
        assignee = User.objects.get(pk=assignee_id)
    except User.DoesNotExist:
        raise BusinessValidationError({"assignee": ["Пользователь не найден."]})

    if not project.is_member(assignee):
        raise BusinessValidationError(
            {"assignee": ["Исполнитель должен быть участником проекта."]}
        )

    return assignee


# ---------------- COMMENT ----------------

def comment_create(*, author: User, task_id: int, text: str) -> Comment:
    try:
        task = Task.objects.get(pk=task_id)
    except Task.DoesNotExist:
        raise BusinessValidationError({"task": ["Задача не найдена."]})

    if not task.project.is_member(author):
        raise PermissionDeniedError("Вы не являетесь участником проекта.")

    return Comment.objects.create(task=task, author=author, text=text)
