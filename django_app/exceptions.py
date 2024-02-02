from django.core.exceptions import ValidationError
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR
)


class LinkDoesNotContainJsonError(ValidationError):
    def __init__(self, link: str, code=HTTP_400_BAD_REQUEST, params=None):
        message = f"There is no dataset by link: {link}"
        super().__init__(message=message, code=code, params=params)


class HttpErrorOnProcessingError(ValidationError):
    def __init__(self, link: str, http_error: str, code=HTTP_400_BAD_REQUEST, params=None):
        message = f"Cannot process dataset by link: {link} - {http_error}"
        super().__init__(message=message, code=code, params=params)


class JsonDecodeError(ValidationError):
    def __init__(self, link: str, code=HTTP_500_INTERNAL_SERVER_ERROR, params=None):
        message = f"There is a problem with the retrieved JSON file by link: {link}"
        super().__init__(message=message, code=code, params=params)


class FileStatusNotFoundError(ValidationError):
    def __init__(self, link: str, code=HTTP_404_NOT_FOUND, params=None):
        message = f"This file was never processed: {link}"
        super().__init__(message=message, code=code, params=params)
