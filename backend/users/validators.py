import re

from django.conf import settings
from rest_framework import serializers


def validate_pattern(username, pattern=settings.REGULAR_EXP):
    '''Проверка юзернейма на соответствие паттерну.'''

    if not re.match(pattern, username):
        raise serializers.ValidationError('Некорректный формат username')


def validate_me(username):
    '''Проверка на использование me в качестве юзернейма.'''

    if username == settings.FORBIDDEN_USERNAME:
        raise serializers.ValidationError(
            'Нельзя использовать "me" в качестве юзернейма!'
        )
