from django.core.exceptions import ValidationError


class LinkDoesNotContainJsonError(ValidationError):
    def __init__(self, link: str, code=None, params=None):
        message = f"There is no dataset by link: {link}"
        super().__init__(message=message, code=code, params=params)


class HttpErrorOnProcessingError(ValidationError):
    def __init__(self, link: str, http_error: str, code=None, params=None):
        message = f"Cannot process dataset by link: {link} - {http_error}"
        super().__init__(message=message, code=code, params=params)


class JsonDecodeError(ValidationError):
    def __init__(self, link: str, code=None, params=None):
        message = f"There is a problem with the retrieved JSON file by link: {link}"
        super().__init__(message=message, code=code, params=params)


class FileStatusNotFoundError(ValidationError):
    def __init__(self, link: str, code=None, params=None):
        message = f"This file was never processed: {link}"
        super().__init__(message=message, code=code, params=params)
