"""Доменные исключения.

Сервисы и селекторы говорят на языке домена ("нельзя", "не найдено",
"невалидно"). В HTTP-коды это переводится в одном месте —
config/exception_handler.py.
"""


class ApplicationError(Exception):
    """Базовое доменное исключение."""


class NotFoundError(ApplicationError):
    """Ресурс не существует или невидим текущему пользователю. -> 404."""


class PermissionDeniedError(ApplicationError):
    """Ресурс виден, но действие запрещено. -> 403."""


class BusinessValidationError(ApplicationError):
    """Данные нарушают бизнес-правило. -> 400."""
