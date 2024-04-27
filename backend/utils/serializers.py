from api.models import Recipe
from rest_framework import serializers


class SimpleRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели Recipe,
    предназначенный для отображения объектов модели в упрощенном виде.
    '''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
