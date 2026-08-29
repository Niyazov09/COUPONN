from django.test import SimpleTestCase

from config.exception_handler import application_exception_handler
from tracker.exceptions import ApplicationError, BusinessValidationError


class ExceptionHandlerTests(SimpleTestCase):
    def test_bare_application_error_does_not_fall_through_to_500(self):
        # Регрессия: ApplicationError, кинутый напрямую (или новый
        # наследник без записи в STATUS_BY_EXCEPTION), уходил в
        # стандартный DRF-хендлер и в итоге превращался в 500.
        response = application_exception_handler(ApplicationError("что-то пошло не так"), {})
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 400)

    def test_known_subclass_still_maps_to_its_own_status(self):
        response = application_exception_handler(
            BusinessValidationError({"field": ["invalid"]}), {}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"field": ["invalid"]})
