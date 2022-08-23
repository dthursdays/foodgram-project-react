from django.contrib import admin

from . import models


class RecipeAdmin(admin.ModelAdmin):
    def favorite_count(self, obj):
        queryset = models.Recipe.is_favorited.through.objects.filter(
            recipe_id=obj.id
        )
        return queryset.count()

    list_display = ('name', 'author')
    list_filter = ('tags', )
    search_fields = ('name', 'author__username')
    readonly_fields = ('favorite_count', )


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient_name', 'ingredient_amount')
    search_fields = ('recipe__name')

    def ingredient_name(self, obj):
        return (f'{obj.ingredient.name} id: {obj.ingredient.id}')

    def ingredient_amount(self, obj):
        return (f'{obj.amount} {obj.ingredient.measurement_unit}')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    search_fields = ('name', 'id')


admin.site.register(models.Tag)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
