from django.contrib import admin

from api.models import Tag

admin.site.empty_value_display = 'Не задано'


@admin.register(Tag)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug', 'color')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    list_filter = ('name', 'slug')