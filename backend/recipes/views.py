from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from . import cart, filters, mixins, models, serializers


class TagViewSet(mixins.ListRetrieveViewSet):
    queryset = models.Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = models.Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    filter_backends = (DjangoFilterBackend, )
    filterset_class = filters.RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.RecipeCreateSerializer
        elif self.action == 'update':
            return serializers.RecipeCreateSerializer
        elif self.action == 'partial_update':
            return serializers.RecipeCreateSerializer
        return serializers.RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = serializers.RecipeSerializer(
            instance,
            context={'request': request}
        )
        headers = self.get_success_headers(instance_serializer.data)
        return Response(instance_serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance,
                                         data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        instance_serializer = serializers.RecipeSerializer(
            instance,
            context={'request': request}
        )

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(instance_serializer.data)

    def perform_update(self, serializer):
        return serializer.save()

    @action(methods=['post', 'delete'], detail=True)
    def favorite(self, request, pk=None):
        try:
            recipe = models.Recipe.objects.get(pk=pk)
        except models.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if recipe in request.user.favorites.all():
                return Response(
                    {'errors': 'Рецепт уже был добавлен в избранное'},
                    status=status.HTTP_400_BAD_REQUEST)
            request.user.favorites.add(recipe)
            serializer = serializers.FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if recipe not in request.user.favorites.all():
                return Response(
                    {'errors': 'Такого рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST)
            request.user.favorites.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True)
    def shopping_cart(self, request, pk=None):
        try:
            recipe = models.Recipe.objects.get(pk=pk)
        except models.Recipe.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if recipe in request.user.shopping_cart.all():
                return Response(
                    {'errors': 'Рецепт уже был добавлен в список покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            request.user.shopping_cart.add(recipe)
            serializer = serializers.FavoriteRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if recipe not in request.user.shopping_cart.all():
                return Response(
                    {'errors': 'Такого рецепта нет в списке покупок'},
                    status=status.HTTP_400_BAD_REQUEST)
            request.user.shopping_cart.remove(recipe)
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def download_shopping_cart(self, request):
        if request.method == 'GET':
            recipes = request.user.shopping_cart.all()
            ingredients = models.IngredientInRecipe.objects.filter(
                recipe__in=recipes
            )
            all_ings = [(i.ingredient.name, i.amount,
                        i.ingredient.measurement_unit) for i in ingredients]
            lines = cart.normalize(all_ings)
            response = HttpResponse(content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=cart.txt'
            response.writelines(lines)
            return response


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, )
    pagination_class = None
    search_fields = ('^name',)
