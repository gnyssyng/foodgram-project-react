from api.models import (Cart, Favorite, Ingredient, IngredientInRecipe, Recipe,
                        Tag)
from django.conf import settings
from django.core.exceptions import ValidationError
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.models import User
from users.serializers import UserSerializer


def raise_validation_error(message):
    '''Вызывает ошибку валидации с переданным в функцию сообщением.'''
    raise ValidationError(message=message)


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
    name = serializers.SerializerMethodField(
        source='ingredient.name'
    )
    measurement_unit = serializers.SerializerMethodField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise ValidationError('Количество не может быть меньше 1.')
        return value

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    '''
    Сериалиазтор модели IngredientInRecipe.

    Сериализатор предназначен для десериализации объектов модели.
    '''

    id = serializers.ReadOnlyField()
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class CartFavoriteMixin(metaclass=serializers.SerializerMetaclass):
    '''
    Миксин для сериализаторов моделей Cart и Favorite.

    Добавляет методы, возвращающие булевы значения нахождения
    объектов(рецептов) в таблицах моделей Cart и Favorite.
    true - если рецепт присутствует в таблице соответствующей модели.
    is_in_shopping_cart - объект есть в пользовательской корзине
    is_favorited - объект есть в списке избранных рецептов
    '''

    def get_is_in_shopping_cart(self, obj):

        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.carts.filter(recipe=obj).exists()
        )

    def get_is_favorited(self, obj):

        request = self.context.get('request')
        return (
            request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )


class RecipeSerializer(serializers.ModelSerializer, CartFavoriteMixin):
    '''
    Сериализатор модели Recipe

    Предназначен для чтения объектов модели.
    '''

    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredient_recipes'
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )


def validate_existence(recipes, model):
    '''Проверяет существуют ли объекты модели.'''
    model_ids = model.objects.values_list('id', flat=True)
    if not set(recipes).issubset(model_ids):
        raise_validation_error(
            f'Несуществующий объект модели {model.__name__}'
        )


def validate_existing_object(value, model):
    '''Проверяет существуют ли объекты модели и не дублируются ли они.'''
    if model == Tag:
        field_ids = [field.id for field in value]
    else:
        field_ids = [field['id'] for field in value]
    validate_existence(field_ids, model)
    if len(field_ids) > len(set(field_ids)):
        raise_validation_error(
            f'Нельзя повторно добавить объект модели {model.__name__}'
        )


class RecipeAddSerializer(serializers.ModelSerializer, CartFavoriteMixin):
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
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    def validate(self, data):
        if not data.get('tags'):
            raise_validation_error(
                'Должен присутствовать как минимум один тэг.'
            )
        elif not data.get('ingredients'):
            raise_validation_error(
                'Должен присутствовать как минимум один ингредиент.'
            )
        elif not data.get('image'):
            raise_validation_error(
                'Нельзя отправить рецепт без фото.'
            )
        elif data.get('cooking_time') < settings.MIN_COOKING_TIME:
            raise_validation_error(
                'Время готовки не может быть'
                f'меньше {settings.MIN_COOKING_TIME}.'
            )
        validate_existing_object(data.get('ingredients'), Ingredient)
        validate_existing_object(data.get('tags'), Tag)
        return super().validate(data)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def create_ingredint_in_recipe(self, ingredients_data, recipe):

        for ingredient in ingredients_data:
            amount = ingredient.get('amount')
            ingredient = ingredient.get('id')
            IngredientInRecipe.objects.create(
                recipe=recipe,
                ingredient=Ingredient(id=ingredient),
                amount=amount
            )

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


def validate_cart_favorite(request, data, model):
    '''Валидация моделей Cart и Favorite

    Проверяет нахождения объекта(рецепта)
    модели(Cart или Favorite) в базе.'''
    if request.method == 'POST':
        if model.objects.filter(
                author=data.get('author'),
                recipe=data.get('recipe').pk
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


class CartSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Cart.'''

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Cart
        fields = ['recipe', 'author']

    def validate(self, data):
        return super().validate(
            validate_cart_favorite(self.context.get('request'), data, Cart)
        )

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': instance.recipe.image.url,
            'cooking_time': instance.recipe.cooking_time
        }


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор модели Favorite.'''

    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())
    author = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )

    class Meta:
        model = Favorite
        fields = ['recipe', 'author']

    def validate(self, data):
        validate_cart_favorite(self.context.get('request'), data, Favorite)
        return super().validate(data)

    def to_representation(self, instance):
        return {
            'id': instance.recipe.id,
            'name': instance.recipe.name,
            'image': instance.recipe.image.url,
            'cooking_time': instance.recipe.cooking_time
        }
