from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Tag(models.Model):
    '''Модель тэгов рецепта.'''

    name = models.CharField(
        'Тэг',
        max_length=settings.CHAR_LENGTH
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.CHAR_LENGTH
    )
    color = ColorField(
        'Цвет',
        unique=True,
        max_length=settings.COLOR_CHAR_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'{self.name}'


class Ingredient(models.Model):
    '''Модель ингредиентов рецепта.'''

    name = models.CharField(
        'Ингредиент',
        max_length=settings.CHAR_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.CHAR_LENGTH
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}'


class Recipe(models.Model):
    '''Модель рецепта.'''

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='recipes'
    )
    name = models.CharField(
        'Рецепт',
        max_length=settings.CHAR_LENGTH,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
    )
    text = models.TextField(
        'Текст'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/images/',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=(
            MinValueValidator(
                settings.MIN_COOKING_TIME,
                'Неккореткное время приготовления. Минимальное время:'
                f'{settings.MIN_COOKING_TIME}.'
            ),
        )
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}'


class IngredientInRecipe(models.Model):
    '''Модель, связывающая модели Recipe и Ingredient.'''

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                settings.MIN_INGREDIENT,
                f'Неккореткное количество ингредиента.'
                f'Минимальное количество: {settings.MIN_INGREDIENT}'
            ),
        )
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецпет',
        on_delete=models.CASCADE,
        related_name='ingredient_recipes'
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        ordering = ('ingredient',)

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    '''Модель избранных рецпетов.'''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        default_related_name = 'favorites'

    def __str__(self):
        return f'{self.recipe}'


class Cart(models.Model):
    '''Модель пользовательской корзины.'''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ('recipe',)
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'
        default_related_name = 'carts'

    def __str__(self):
        return f'{self.recipe}'
