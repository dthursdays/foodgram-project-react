from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from users.serializers import CustomUserSerializer
from .models import Ingredient, IngredientInRecipe, Recipe, Tag

User = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')


class IngredientInRecipeCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientInRecipe
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = CustomUserSerializer(many=False)
    ingredients = serializers.SerializerMethodField()
    image = Base64ImageField(max_length=None, use_url=True)
    is_favorited = serializers.SerializerMethodField(default=False)
    is_in_shopping_cart = serializers.SerializerMethodField(default=False)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )

    def get_ingredients(self, obj):
        queryset = IngredientInRecipe.objects.filter(recipe=obj.id)
        serializer = IngredientInRecipeSerializer(queryset, many=True)
        return serializer.data

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            user.favorites.filter(id=obj.id).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return (
            user.is_authenticated and
            user.shopping_cart.filter(id=obj.id).exists()
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientInRecipeCreateSerializer(many=True, required=True)
    image = Base64ImageField(required=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'ingredients', 'name',
                  'text', 'image', 'cooking_time')

    def add_ingredients(self, recipe, ingredients):
        if ingredients:
            recipe.ingredients.clear()
            IngredientInRecipe.objects.bulk_create(
                [
                    IngredientInRecipe(
                        ingredient=ingredient['id'],
                        recipe=recipe,
                        amount=ingredient['amount']
                    )
                    for ingredient in ingredients
                ]
            )

    def add_tags(self, recipe, tags):
        if tags:
            recipe.tags.clear()
            for tag in tags:
                recipe.tags.add(tag)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Должен быть указан хотя бы один ингредиент'}
            )

        ingredients_set = set(ing.get('id') for ing in ingredients)
        if len(ingredients) != len(ingredients_set):
            raise serializers.ValidationError(
                {'ingredients': 'Ингридиенты должны быть уникальными'}
            )

        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Должен быть указан хотя бы один тэг'}
            )

        tags_set = set(tag for tag in tags)
        if len(tags) != len(tags_set):
            raise serializers.ValidationError(
                {'tags': 'Тэги должны быть уникальными'}
            )
        return data

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        recipe = Recipe.objects.create(**validated_data)
        self.add_ingredients(recipe, ingredients)
        self.add_tags(recipe, tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self.add_ingredients(instance, ingredients)
        self.add_tags(instance, tags)
        return instance


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
