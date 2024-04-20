from django.contrib import admin

from api.models import Cart, Favorite, Ingredient, Recipe, Tag
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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'text', 'tags_display', 'author',
        'ingredients_display', 'pub_date', 'image', 'cooking_time'
    )
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'author', 'tags')

    def tags_display(self, obj):
        return ', '.join([tag.slug for tag in obj.tags.all()])
    tags_display.short_description = 'Тэги'

    def ingredients_display(self, obj):
        return ', '.join(
            [ingredient.name for ingredient in obj.ingredients.all()]
        )
    tags_display.short_description = 'Ингредиенты'


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
        'last_name', 'get_superuser_staff'
    )
    search_fields = ('username', )
    list_filter = ('username', 'email')

    def get_superuser_staff(self, obj):

        if obj.is_superuser:
            return 'Суперпользователь'
        elif obj.is_staff:
            return 'Стафф'
        else:
            return 'Пользователь'
    get_superuser_staff.short_description = 'Пользовательская роль'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'following')
    list_filter = ('user', 'following')
    search_fields = ('user', 'following')
