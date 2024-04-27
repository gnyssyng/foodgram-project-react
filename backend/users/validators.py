import re

from rest_framework import serializers


def validate_pattern(username, pattern=r"^[\w.@+-]+$"):
    '''Проверка юзернейма на соответствие паттерну.'''

    if not re.match(pattern, username):
        raise serializers.ValidationError('Некорректный формат username')


def validate_me(username):
    '''Проверка на использование me в качестве юзернейма.'''

    if username == 'me':
        raise serializers.ValidationError(
            'Нельзя использовать "me" в качестве юзернейма!'
        )
