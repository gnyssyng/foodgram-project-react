import base64

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from rest_framework import serializers

from api.models import (
    Cart, Favorite, Ingredient, IngredientInRecipe,
    Recipe, Tag
)
from users.models import Follow
from users.serializers import CustomUserSerializer


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


class Base64ImageField(serializers.ImageField):
    '''Сериализатор, преобразующий картинку в набор символов.'''

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class IngredientInRecipeAddSerializer(serializers.ModelSerializer):
    '''
    Сериалиазтор модели IngredientInRecipe,
    предназначенный для добавления новых объектов модели.
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
    Сериалиазтор модели IngredientInRecipe,
    предназначенный для чтения объектов модели.
    '''

    id = serializers.IntegerField()
    name = serializers.SerializerMethodField(source='ingredient.name')
    measurement_unit = serializers.SerializerMethodField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class CartFavoriteMixin(metaclass=serializers.SerializerMetaclass):
    '''
    Миксин, предзначенный для добавления полей is_in_shopping_cart и
    is_favorited
    '''

    def get_is_in_shopping_cart(self, obj):

        request = self.context.get('request')
        if request.user.is_authenticated:
            user = request.user
            in_cart = Cart.objects.filter(
                author=user,
                recipe=obj
            ).exists()
            return in_cart
        return False

    def get_is_favorited(self, obj):

        request = self.context.get('request')
        if request.user.is_authenticated:
            user = request.user
            in_cart = Favorite.objects.filter(
                author=user,
                recipe=obj
            ).exists()
            return in_cart
        return False


class RecipeSerializer(serializers.ModelSerializer, CartFavoriteMixin):
    '''
    Сериализатор модели Recipe,
    предназначенный для чтения объектов модели.
    '''

    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    tags = TagSerializer(read_only=True, many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        many=True,
        source='ingredientrecipes'
    )
    image_url = serializers.SerializerMethodField(
        'get_image_url',
        read_only=True,
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image',
            'image_url', 'text', 'cooking_time'
        )

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


def raise_recipe_error(message):
    raise ValidationError(message=message)


def validate_tag_ingredient(value, model, message_1, message_2):
    field_ids = []
    for field in value:
        if model == Tag:
            field_id = field.pk
        else:
            field_id = field['id']
        if field_id not in field_ids:
            field_ids.append(field_id)
        else:
            raise_recipe_error(
                f'{message_1}'
            )
        try:
            model.objects.get(id=field_id)
        except model.DoesNotExist:
            raise_recipe_error(
                f'{message_2}'
            )


class RecipeAddSerializer(serializers.ModelSerializer, CartFavoriteMixin):
    '''
    Сериализатор модели Recipe, предназначенный для записи объектов модели.
    '''

    image = Base64ImageField(required=True, allow_null=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    ingredients = IngredientInRecipeAddSerializer(
        many=True,
        source='ingredientrecipes'
    )
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def validate_ingredients(self, value):
        if not value:
            raise_recipe_error(
                'Должен присутствовать как минимум один ингредиент.'
            )
        validate_tag_ingredient(
            value, Ingredient,
            'Нельзя добавить одни и те же ингредиенты дважды.',
            'Указанного ингредиента не существут.'
        )
        return value

    def validate_tags(self, value):
        if not value:
            raise_recipe_error(
                'Должен присутствовать как минимум один тэг.'
            )
        validate_tag_ingredient(
            value, Tag,
            'Нельзя добавить одни и те же тэги дважды.',
            'Указанного тэга не существут.'
        )
        return value

    def validate_cooking_time(self, value):
        if value < 1:
            raise_recipe_error(
                'Время готовки не может быть меньше 1.'
            )
        return value

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
        ingredients_data = validated_data.pop('ingredientrecipes')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredint_in_recipe(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredientrecipes')
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


class SimpleRecipeReadSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для модели Recipe,
    предназначенный для отображения объектов модели в упрощенном виде.
    '''

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']


class FollowSerializer(serializers.ModelSerializer):
    '''Сериализатор для модели Follow.'''

    following = CustomUserSerializer()

    class Meta:
        model = Follow
        fields = ['following', ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        following_user = data['following']
        recipes = self.context.get('recipes', {})
        following_user_recipes = recipes.filter(
            author=following_user['id']
        )[:self.context.get('recipes_limit')]
        return {
            'email': following_user['email'],
            'id': following_user['id'],
            'username': following_user['username'],
            'first_name': following_user['first_name'],
            'last_name': following_user['last_name'],
            'is_subscribed': following_user['is_subscribed'],
            'recipes': SimpleRecipeReadSerializer(
                following_user_recipes,
                many=True,
                context={'request': self.context.get('request')}
            ).data,
            'recipes_count': len(following_user_recipes)
        }
