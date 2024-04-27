from api.filters import RecipeFilter
from api.models import Cart, Favorite, Ingredient, Recipe, Tag
from api.permissions import IsAuthor
from api.serializers import (CartSerializer, FavoriteSerializer,
                             IngredientSerializer, RecipeAddSerializer,
                             RecipeSerializer, TagSerializer)
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from utils.views import response_400_recipe


class TagViewSet(ReadOnlyModelViewSet):

    pagination_class = None
    permission_classes = (AllowAny,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):

    pagination_class = None
    permission_classes = [AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer

    def get_queryset(self):
        queryset = self.queryset
        name_starts_with = self.request.query_params.get('name', None)
        if name_starts_with:
            queryset = queryset.filter(name__istartswith=name_starts_with)
        return queryset


class RecipeViewSet(ModelViewSet):

    ERRORS = {
        'not_exists': 'Рецепта с таким id не существует.',
        'already_exists': 'Нельзя дважды добавить одно и то же.',
        'not_in_cart_favorite': 'Рецепт с таким id не был добавлен.'
    }

    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthor]

    def get_queryset(self):
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'ingredients'
        )
        if not self.request.user.is_authenticated:
            return queryset.all()
        return (
            queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        recipe=OuterRef('id'),
                        author=self.request.user
                    )
                ),
                is_in_shopping_cart=Exists(
                    Cart.objects.filter(
                        recipe=OuterRef('id'),
                        author=self.request.user
                    )
                )
            ).all()
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeAddSerializer

    def get_shopping_cart_queryset(self, request):
        '''Возвращает queryset для скачивания списка покупок.'''
        cart_recipes = Cart.objects.filter(
            author=request.user
        ).values_list('recipe', flat=True)
        ingredients_amount = Recipe.objects.filter(
            id__in=cart_recipes
        ).prefetch_related(
            'ingredients'
        ).values(
            'ingredients__name',
            'ingredients__measurement_unit'
        ).annotate(
            amount=Sum('ingredient_recipes__amount')
        ).order_by('ingredients__name')
        return ingredients_amount

    @action(['GET'], detail=False, name='download-shopping-cart')
    def download_shopping_cart(self, request):
        '''Подготавлиет к скачиванию файл со списком покупок.'''
        queryset = self.get_shopping_cart_queryset(request)
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        for ingredient in queryset:
            response.write(
                f'{ingredient["ingredients__name"]}: '
                f'{ingredient["amount"]}'
                f'{ingredient["ingredients__measurement_unit"]}\n'
            )
        return response

    def post_delete_favorite_cart(self, request, pk, model):
        if request.method == 'POST':
            try:
                recipe = Recipe.objects.get(id=pk)
            except Recipe.DoesNotExist:
                return response_400_recipe('Несуществующий рецепт.')
        else:
            recipe = get_object_or_404(Recipe, id=pk)
        data = {'recipe': recipe.id, 'author': request.user.id}
        if model == Cart:
            serializer = CartSerializer(
                data=data,
                context={'request': request}
            )
        elif model == Favorite:
            serializer = FavoriteSerializer(
                data=data,
                context={'request': request}
            )
        serializer.is_valid(raise_exception=True)
        if request.method == 'POST':
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        get_object_or_404(
            model,
            recipe=serializer.validated_data.get('recipe'),
            author=request.user
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(['POST', 'DELETE'], detail=True, name='shopping-cart')
    def shopping_cart(self, request, pk):
        return self.post_delete_favorite_cart(request, pk, Cart)

    @action(['POST', 'DELETE'], detail=True, name='favorite')
    def favorite(self, request, pk):
        return self.post_delete_favorite_cart(request, pk, Favorite)
