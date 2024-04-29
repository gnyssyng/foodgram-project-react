from django.conf import settings
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from api.models import (Cart, Favorite, Ingredient, IngredientInRecipe, Recipe,
                        Tag)
from users.serializers import UserSerializer
from utils.serializers import (SimpleRecipeSerializer, raise_validation_error,
                               validate_cart_favorite,
                               validate_existing_object)


class TagSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Tag.'''

    class Meta:
        model = Tag
        fields = ('id', 'slug', 'color', 'name')


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериалиазтор модели Ingredient.'''

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)


class IngredientInRecipeAddSerializer(serializers.ModelSerializer):
    '''
    Сериалиазтор модели IngredientInRecipe.


    Сериализатор предназначен для сериализации новых объектов модели.
    '''

    id = serializers.IntegerField(write_only=True)
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < settings.MIN_AMOUNT:
            raise ValidationError(
                f'Количество не может быть меньше {settings.MIN_AMOUNT}.'
            )
        return value

    def validate(self, data):
        try:
            Ingredient.objects.get(id=data.get('id'))
        except Ingredient.DoesNotExist:
            raise_validation_error('Несуществующий ингредиент')
        return super().validate(data)


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериалиазтор модели IngredientInRecipe.

    Сериализатор предназначен для десериализации объектов модели.
    '''

    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe

    Предназначен для чтения объектов модели.
    '''

    is_in_shopping_cart = serializers.BooleanField(default=False)
    is_favorited = serializers.BooleanField(default=False)
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipes'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'name', 'image', 'text', 'cooking_time',
            'is_in_shopping_cart', 'is_favorited'
        )


class RecipeAddSerializer(serializers.ModelSerializer):
    '''
    Сериализатор модели Recipe.

    Предназначен для записи объектов модели.
    '''

    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True, required=True
    )
    ingredients = IngredientInRecipeAddSerializer(
        many=True, required=True
    )
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'name', 'image',
            'text', 'cooking_time',
        )

    def validate(self, data):
        ingredients = data.get('ingredients')
        tags = data.get('tags')
        if not tags:
            raise_validation_error(
                'Должен присутствовать как минимум один тэг.'
            )
        elif not ingredients:
            raise_validation_error(
                'Должен присутствовать как минимум один ингредиент.'
            )
        elif not data.get('image'):
            raise_validation_error(
                'Нельзя отправить рецепт без фото.'
            )
        elif (
            data.get('cooking_time') < settings.MIN_COOKING_TIME
            or data.get('cooking_time') > settings.MAX_COOKING_TIME
        ):
            raise_validation_error(
                'Время готовки не может быть '
                f'меньше {settings.MIN_COOKING_TIME} '
                f'или больше {settings.MAX_COOKING_TIME}'
            )
        validate_existing_object(ingredients, Ingredient)
        validate_existing_object(tags, Tag)
        return super().validate(data)

    def create_ingredint_in_recipe(self, ingredients_data, recipe):
        ingredients = []
        for ingredient in ingredients_data:
            amount = ingredient.get('amount')
            ingredient = ingredient.get('id')
            ingredients.append(
                IngredientInRecipe(
                    recipe=recipe,
                    ingredient_id=ingredient,
                    amount=amount
                )
            )
        IngredientInRecipe.objects.bulk_create(ingredients)

    def create(self, validated_data):
        validated_data.update(
            {
                'author':
                self.context["request"].user
            }
        )
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredint_in_recipe(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredint_in_recipe(ingredients_data, instance)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={'request': self.context.get('request')}
        ).data
        return serializer


class CartSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Cart.'''

    class Meta:
        model = Cart
        fields = ['recipe', 'author']

    def validate(self, data):
        validate_cart_favorite(self.context.get('request'), data, Cart)
        return super().validate(data)

    def to_representation(self, instance):
        return SimpleRecipeSerializer(
            instance.recipe
        ).data


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Favorite.'''

    class Meta:
        model = Favorite
        fields = ['recipe', 'author']

    def validate(self, data):
        validate_cart_favorite(self.context.get('request'), data, Favorite)
        return super().validate(data)

    def to_representation(self, instance):
        return SimpleRecipeSerializer(
            instance.recipe
        ).data
