from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import CustomUserSerializer

from . import models

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    measurement_unit = serializers.SerializerMethodField()

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_id(self, obj):
        return obj.ingredient.id

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=models.Ingredient.objects.all()
    )

    class Meta:
        model = models.IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(many=False)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(required=True)
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = models.Recipe
        fields = ('id', 'tags', 'author', 'ingredients', 'is_favorited',
                  'is_in_shopping_cart', 'name', 'image', 'text',
                  'cooking_time')

    def get_ingredients(self, obj):
        ing_amounts = models.IngredientInRecipe.objects.filter(
            recipe=obj.id)
        serializer = IngredientInRecipeSerializer(ing_amounts, many=True)

        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                user.favorites.filter(id=obj.id).exists())

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (user.is_authenticated and
                user.shopping_cart.filter(id=obj.id).exists())


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True, required=True)
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=models.Tag.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = models.Recipe
        fields = ('tags', 'ingredients', 'name',
                  'text', 'image', 'cooking_time')

    def add_ingredients_tags(self, recipe, ingredients, tags):
        if ingredients:
            recipe.ingredients.clear()
            models.IngredientInRecipe.objects.bulk_create(
                [models.IngredientInRecipe(
                    ingredient=ingredient['id'],
                    recipe=recipe,
                    amount=ingredient['amount']
                ) for ingredient in ingredients]
            )

        if tags:
            recipe.tags.clear()
            for tag in tags:
                recipe.tags.add(tag)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError({'ingredients':
                                               'Должен быть указан '
                                               'хотя бы один ингредиент'})

        ingredients_set = set(ing.get('id') for ing in ingredients)
        if len(ingredients) != len(ingredients_set):
            raise serializers.ValidationError({'ingredients':
                                               'Ингридиенты должны '
                                               'быть уникальными'})

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError({'tags':
                                               'Должен быть указан '
                                               'хотя бы один тэг'})

        tags_set = set(tag for tag in tags)
        if len(tags) != len(tags_set):
            raise serializers.ValidationError({'tags':
                                               'Тэги должны быть уникальными'})
        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = models.Recipe.objects.create(**validated_data)
        self.add_ingredients_tags(recipe, ingredients, tags)

        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        self.add_ingredients_tags(instance, ingredients, tags)

        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
