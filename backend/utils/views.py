from rest_framework import status
from rest_framework.response import Response


def response_400(message):
    '''Возвращает статус 400 и сообщение об ошибке.'''
    return Response(
        {'errors': f'{message}'},
        status=status.HTTP_400_BAD_REQUEST
    )


def response_404_recipe(message):
    '''Возвращает статус 404 и сообщение об ошибке.'''
    return Response(
        {'errors': f'{message}'},
        status=status.HTTP_404_NOT_FOUND
    )
