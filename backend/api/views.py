from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import RecipeFilter
from api.models import (Cart, Favorite, Ingredient, IngredientInRecipe, Recipe,
                        Tag)
from api.permissions import IsAuthor
from api.serializers import (IngredientSerializer, RecipeAddSerializer,
                             RecipeSerializer, SimpleRecipeReadSerializer,
                             TagSerializer)


class TagViewSet(ReadOnlyModelViewSet):

    pagination_class = None
    permission_classes = [AllowAny, ]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def retrieve(self, request, pk=None):
        queryset = Tag.objects.all()
        tag = get_object_or_404(queryset, pk=pk)
        serializer = TagSerializer(tag)
        return Response(serializer.data)


class IngredientViewSet(ReadOnlyModelViewSet):

    pagination_class = None
    permission_classes = [AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def retrieve(self, request, pk=None):
        tag = get_object_or_404(self.queryset, pk=pk)
        serializer = IngredientSerializer(tag)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = self.queryset
        name_starts_with = self.request.query_params.get('name', None)
        if name_starts_with:
            queryset = queryset.filter(name__istartswith=name_starts_with)
        return queryset


def response_400_recipe(message):
    return Response(
        {'errors': f'{message}'},
        status=status.HTTP_400_BAD_REQUEST
    )


class RecipeViewSet(ModelViewSet):

    ERRORS = {
        'not_exists': 'Рецепта с таким id не существует.',
        'already_exists': 'Нельзя дважды добавить одно и то же.',
        'not_in_cart_favorite': 'Рецепт с таким id не был добавлен.'
    }

    queryset = Recipe.objects.all()
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        limit = self.request.query_params.get('limit', None)
        if limit:
            queryset = queryset[:int(limit)]
        return queryset

    def get_permissions(self):
        if self.request.method == 'PATCH':
            return [IsAuthor(), ]
        if self.request.method == 'DELETE':
            return [IsAuthor(), ]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeAddSerializer

    def retrieve(self, request, pk):
        try:
            instance = self.get_object()
        except Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def partial_update(self, request, pk):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(['GET'], detail=False, name='download-shopping-cart')
    def download_shopping_cart(self, request):
        user = request.user
        cart_recipes = Cart.objects.filter(
            author=user
        ).values_list('recipe', flat=True)
        cart = {}
        for recipe_id in cart_recipes:
            recipe = get_object_or_404(Recipe, id=recipe_id)
            for ingredient in recipe.ingredients.all():
                amount = IngredientInRecipe.objects.get(recipe=recipe).amount
                if ingredient.name not in cart:
                    cart[ingredient.name] = amount
                else:
                    cart[ingredient.name] += amount
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        for ingredient, amount in cart.items():
            unit = Ingredient.objects.get(name=ingredient).measurement_unit
            response.write(f'{ingredient}: {amount} {unit}\n')
        return response

    def post_delete_favorite_cart(self, request, pk, model):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не авторизирован.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return response_400_recipe(self.ERRORS.get('not_exists'))
            if model.objects.filter(
                    author=user, recipe=recipe
            ).exists():
                return response_400_recipe(self.ERRORS.get('already_exists'))
            else:
                model.objects.create(
                    author=user, recipe=recipe
                )
            serializer = SimpleRecipeReadSerializer(recipe)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        elif self.request.method == 'DELETE':
            recipe = get_object_or_404(Recipe, id=pk)
            try:
                cart_favorite = model.objects.get(recipe_id=pk, author_id=user)
                cart_favorite.delete()
            except model.DoesNotExist:
                return response_400_recipe(
                    self.ERRORS.get('not_in_cart_favorite')
                )
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST', 'DELETE'], detail=True, name='shopping-cart')
    def shopping_cart(self, request, pk):
        return self.post_delete_favorite_cart(request, pk, Cart)

    @action(['POST', 'DELETE'], detail=True, name='favorite')
    def favorite(self, request, pk):
        return self.post_delete_favorite_cart(request, pk, Favorite)
