from rest_framework.response import Response
from rest_framework.views import exception_handler

from tracker.exceptions import (
    BusinessValidationError,
    NotFoundError,
    PermissionDeniedError,
)

STATUS_BY_EXCEPTION = {
    BusinessValidationError: 400,
    PermissionDeniedError: 403,
    NotFoundError: 404,
}


def application_exception_handler(exc, context):
    """Переводит доменные исключения в HTTP-ответы.

    Всё остальное (DRF-исключения, 401 и т.д.) отдаём стандартному
    exception_handler DRF без изменений.
    """
    for exc_class, status_code in STATUS_BY_EXCEPTION.items():
        if isinstance(exc, exc_class):
            detail = exc.args[0] if exc.args else "Ошибка."
            data = detail if isinstance(detail, dict) else {"detail": detail}
            return Response(data, status=status_code)

    return exception_handler(exc, context)
