from django_filters import rest_framework as filters

from api.models import Recipe


class RecipeFilter(filters.FilterSet):
    '''
    Фильтр модели рецепта, в котором реализаована
    возможность филтрации рецептов по автору, множественным тэгам,
    а так же по тому находится ли рецепт в пользовательской корзине
    или избранном.
    '''

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    author = filters.NumberFilter(field_name='author_id')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                recipes_favourites__author=self.request.user
            )
        else:
            return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                recipes_cart__author=self.request.user
            )
        else:
            return queryset
