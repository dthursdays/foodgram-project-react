from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )

    color = ColorField(
        unique=True,
        blank=False,
        null=False
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False
    )

    measurement_unit = models.CharField(
        max_length=200
    )

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):

    ingredient = models.ForeignKey(
        Ingredient,
        related_name='amounts',
        on_delete=models.CASCADE
    )

    recipe = models.ForeignKey(
        'Recipe',
        related_name='ingredients_amounts',
        on_delete=models.CASCADE
    )

    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1)
        ]
    )

    def __str__(self):
        return self.ingredient.name


class Recipe(models.Model):

    name = models.CharField(
        max_length=200,
        blank=False,
        null=False
    )

    text = models.TextField(
        blank=False,
        null=False
    )

    cooking_time = models.PositiveSmallIntegerField(
        blank=False,
        null=False,
        validators=[
            MinValueValidator(1)
        ]
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes'
    )

    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=False
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through=IngredientInRecipe
    )

    image = models.ImageField(
        upload_to='recipes/', null=False, blank=False
    )

    is_favorited = models.ManyToManyField(
        User,
        related_name='favorites'
    )

    is_in_shopping_cart = models.ManyToManyField(
        User,
        related_name='shopping_cart'
    )

    class Meta:
        ordering = ('-id',)
