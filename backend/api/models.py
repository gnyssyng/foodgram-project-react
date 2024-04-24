from colorfield.fields import ColorField
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from users.models import CustomUser


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
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug', 'color'],
                name='unique_tag'
            )
        ]
        ordering = ['id']
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
        ordering = ['id']
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
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        'Рецепт',
        max_length=settings.CHAR_LENGTH,
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='ingredients',
    )
    text = models.TextField(
        'Текст'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipe/images/',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления',
        validators=[
            MinValueValidator(
                0,
                'Неккореткное время приготовления.'
                'Время приготовления должно быть больше 0.'
            ),
        ]
    )

    class Meta:
        ordering = ['-pub_date']
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
        related_name='ingredientrecipes'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(
                0,
                'Неккореткное количество ингредиента.'
                'Количество должно быть больше 0.'
            ),
        ]
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецпет',
        on_delete=models.CASCADE,
        related_name='ingredientrecipes'
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.recipe}'


class Favorite(models.Model):
    '''Модель избранных рецпетов.'''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipes_favourites',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='author_favourites',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.recipe}'


class Cart(models.Model):
    '''Модель пользовательской корзины.'''

    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        related_name='recipes_cart',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='author_cart',
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзине'

    def __str__(self):
        return f'{self.recipe}'
