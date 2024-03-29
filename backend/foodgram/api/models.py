from django.db import models
from users.models import CustomUser
from django.conf import settings


class Tag(models.Model):

    name = models.CharField(
        'Тэг',
        max_length=settings.CHAR_LENGTH
    )
    slug = models.SlugField(
        'Слаг',
        max_length=settings.CHAR_LENGTH
    )
    color = models.CharField(
        'Цвет',
        max_length=settings.COLOR_CHAR_LENGTH
    )

    class Meta:

        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug', 'color'],
                name='unique_tag'
            )
        ]


class Ingredient(models.Model):

    name = models.CharField(
        'Ингредиент',
        max_length=settings.CHAR_LENGTH
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=settings.CHAR_LENGTH
    )


class Recepie(models.Model):

    tags = models.ForeignKey(
        Tag,
        verbose_name='Тэги',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    name = models.CharField(
        'Рецепт',
        max_length=settings.CHAR_LENGTH
    )
    ingredients = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиенты',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    image = models.ImageField(
        upload_to='recepie/images/',
    )


class IngredientInRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Ингредиент',
        on_delete=models.CASCADE
    )
    recepie = models.ForeignKey(
        Recepie,
        verbose_name='Рецепт',
        on_delete=models.CASCADE
    )
    amount = models.PositiveSmallIntegerField(
        'Количество'
    )


class Favourites(models.Model):

    recepie = models.ForeignKey(
        Recepie,
        verbose_name='Рецепт',
        related_name='recepies',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        CustomUser,
        verbose_name='Автор',
        related_name='author',
        on_delete=models.CASCADE
    )
