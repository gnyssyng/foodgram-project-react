from django.core.exceptions import ValidationError
from rest_framework import serializers

from api.models import Recipe, Tag


def raise_validation_error(message):
    '''Вызывает ошибку валидации с переданным в функцию сообщением.'''
    raise ValidationError(message=message)


def validate_existing_object(value, model):
    '''Проверяет существуют ли объекты модели и не дублируются ли они.'''
    if model == Tag:
        field_ids = value
    else:
        field_ids = [field['id'] for field in value]
    if len(field_ids) > len(set(field_ids)):
        raise_validation_error(
            f'Нельзя повторно добавить объект модели {model.__name__}'
        )


def validate_cart_favorite(request, data, model):
    '''Валидация моделей Cart и Favorite

    Проверяет нахождения объекта(рецепта)
    модели(Cart или Favorite) в базе.'''
    if request.method == 'POST':
        if model.objects.filter(
                author=data.get('author'),
                recipe=data.get('recipe').id
        ).exists():
            return raise_validation_error(
                'Нельзя добавить дважды один и тот же объект'
            )
        return data
    try:
        model.objects.get(
            recipe=data.get('recipe'),
            author=data.get('author')
        )
    except model.DoesNotExist:
        return raise_validation_error(
            f'Не существует такого объекта модели {model.__name__}'
        )
    return data


class SimpleRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели Recipe,
    предназначенный для отображения объектов модели в упрощенном виде.
    '''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
