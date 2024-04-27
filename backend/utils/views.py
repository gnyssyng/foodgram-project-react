from rest_framework import status
from rest_framework.response import Response


def response_400_recipe(message):
    '''Возвращает статус 400 и сообщение об ошибке.'''
    return Response(
        {'errors': f'{message}'},
        status=status.HTTP_400_BAD_REQUEST
    )
