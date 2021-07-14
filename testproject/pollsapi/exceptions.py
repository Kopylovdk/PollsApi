from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'ValidationError': _handle_generic_error,
        'IntegrityError': _handle_integrity_error
    }
    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def _handle_generic_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response


def _handle_integrity_error(exc, context, response):
    if not response:
        response = Response({
            'errors': "Ошибка БД. Запись существует."
        }, status=status.HTTP_400_BAD_REQUEST)
    return response
