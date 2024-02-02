from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.response import Response
from rest_framework import exceptions as drf_exceptions
from rest_framework.views import exception_handler


def custom_exception_handler(exc, ctx):
    """
    Formats exceptions' messages into the following format:
    {
        "message": "User-friendly error message"
    }
    """
    response = exception_handler(exc, ctx)

    if isinstance(exc, DjangoValidationError):
        return handle_django_validation_error(exc, ctx, response)

    elif issubclass(type(exc), drf_exceptions.APIException):
        return handle_drf_exceptions(exc, ctx, response)

    else:
        return handle_unknown_exception(exc, ctx, response)


def handle_django_validation_error(exc, ctx, response):
    error_data = None
    if hasattr(exc, "message_dict") and hasattr(exc, "messages"):
        if "__all__" in exc.message_dict and len(exc.message_dict) == 1:
            messages = exc.message_dict.pop("__all__")
            error_data = {"message": ", ".join(messages)}
        else:
            error_data = {"message": exc.message_dict}
    elif hasattr(exc, "message"):
        error_data = {"message": exc.message}
    elif hasattr(exc, "messages"):
        error_data = {"message": ", ".join(exc.messages)}
    return Response(error_data, status=exc.code)


def handle_drf_exceptions(exc, ctx, response):
    # Handle other DRF errors separately and transform their 'detail' attribute into 'message'.
    if hasattr(exc, "detail"):
        response.data["message"] = exc.detail
        del response.data["detail"]
        return response


def handle_unknown_exception(exc, ctx, response):
    # If unexpected error occurs (server error, etc.) we return None as response and
    # it will be re-raised and Django will return a standard HTTP 500 'server error' response.
    if response is None:
        return response
