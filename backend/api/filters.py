from django_filters import rest_framework as filters

from api.models import Ingredient, Recipe


class RecipeFilter(filters.FilterSet):
    '''Фильтр модели рецепта.

    В данном фильтре котором реализаована возможность фильтрации рецептов
    по автору, множественным тэгам.
    Метод filter_is_favorited в качестве аргумента принимает queryset
    и возвращает объекты, добавленные в избранное.
    Метод filter_is_in_shopping_cart в качестве аргумента принимает queryset
    возвращает объекты, добавленные в пользовательскую корзину.
    '''

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author_id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = [
            'tags', 'author', 'name', 'is_favorited', 'is_in_shopping_cart'
        ]

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorites__author=self.request.user
            )
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                carts__author=self.request.user
            )
        return queryset


class IngredientFilter(filters.FilterSet):

    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']
