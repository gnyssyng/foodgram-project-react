from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from api.models import (Cart, Favorite, Ingredient, IngredientInRecipe, Recipe,
                        Tag)
from users.models import Follow, User

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
    min_num = settings.MIN_INGREDIENT
    fields = ('ingredient', 'amount')


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


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'id', 'email', 'username', 'first_name',
        'last_name',
    )
    search_fields = ('username',)
    list_filter = ('username', 'email')


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    search_fields = ('user__username', 'following__username')
