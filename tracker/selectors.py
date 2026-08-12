"""Все чтения домена.

Контракт: keyword-only аргументы, type hints, первый аргумент — user
(почти любое чтение зависит от того, кто смотрит). Возвращает QuerySet
для списков и объект для деталей. Не найдено/невидимо -> NotFoundError.
Никаких изменений данных.
"""
from django.contrib.auth.models import User
from django.db.models import QuerySet

from .exceptions import NotFoundError
from .models import Comment, Project, Task


def project_list(*, user: User) -> QuerySet[Project]:
    return Project.objects.visible_to(user)


def project_get(*, user: User, project_id: int) -> Project:
    try:
        return Project.objects.visible_to(user).get(pk=project_id)
    except Project.DoesNotExist:
        raise NotFoundError("Проект не найден.")


def task_list(*, user: User) -> QuerySet[Task]:
    return Task.objects.visible_to(user).with_priority_order()


def task_get(*, user: User, task_id: int) -> Task:
    try:
        return Task.objects.visible_to(user).get(pk=task_id)
    except Task.DoesNotExist:
        raise NotFoundError("Задача не найдена.")


def task_comment_list(*, user: User, task_id: int) -> QuerySet[Comment]:
    # Невидимая/несуществующая задача -> NotFoundError, до похода за
    # комментариями.
    task = task_get(user=user, task_id=task_id)
    return Comment.objects.filter(task=task)


def comment_list(*, user: User) -> QuerySet[Comment]:
    return Comment.objects.visible_to(user)
