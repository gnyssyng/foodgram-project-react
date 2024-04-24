from django.contrib import admin
from django.apps import apps

from api.models import (
    Cart, Favorite, Ingredient, Recipe,
    Tag, IngredientInRecipe
)
from users.models import CustomUser, Follow

admin.site.empty_value_display = 'Не задано'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)


class TagInLine(admin.TabularInline):
    model = apps.get_model('api.recipe_tags')


class IngredientInLine(admin.TabularInline):
    model = IngredientInRecipe


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [TagInLine, IngredientInLine]
    list_display = (
        'id', 'name', 'text', 'author', 'tags_display',
        'ingredients_display', 'pub_date', 'image', 'cooking_time'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    @admin.display(description='Тэги')
    def tags_display(self, obj):
        return ', '.join([tag.slug for tag in obj.tags.all()])

    @admin.display(description='Ингредиенты')
    def ingredients_display(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'author')
    list_filter = ('recipe', 'author')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'author')
    list_filter = ('recipe', 'author')


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name',
        'last_name',
    )
    search_fields = ('username', )
    list_filter = ('username', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    search_fields = ('user', 'following')
