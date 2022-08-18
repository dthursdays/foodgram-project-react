from django.contrib import admin

from . import models


class RecipeAdmin(admin.ModelAdmin):
    def favorite_count(self, obj):
        queryset = models.Recipe.is_favorited.through.objects.filter(recipe_id=obj.id)
        return queryset.count()

    list_display = ('name', 'author')
    list_filter = ('tags', )
    readonly_fields = ('favorite_count', )


class IngredientInRecipeAdmin(admin.ModelAdmin):
    list_display = ('name_and_id', 'amount_and_mu', 'recipe')

    def name_and_id(self, obj):
        return (f'{obj.ingredient.name} id:{obj.ingredient.id}')

    def amount_and_mu(self, obj):
        return (f'{obj.amount} {obj.ingredient.measurement_unit}')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')


admin.site.register(models.Tag)
admin.site.register(models.Ingredient, IngredientAdmin)
admin.site.register(models.IngredientInRecipe, IngredientInRecipeAdmin)
admin.site.register(models.Recipe, RecipeAdmin)
