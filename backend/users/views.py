from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Follow
from .serializers import UserFollowSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):

    queryset = User.objects.all()
    http_method_names = ['get', 'post', 'delete']

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id=None):
        try:
            author = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            if request.user.follows.filter(author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST)
            if author == request.user:
                return Response(
                    {'errors': 'Вы не можете подписаться сами на себя'},
                    status=status.HTTP_400_BAD_REQUEST)

            Follow.objects.create(user=request.user, author=author)
            serializer = UserFollowSerializer(author,
                                              context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if not request.user.follows.filter(author=author).exists():
                return Response(
                    {'errors': 'Этого пользователя нет в ваших подписках'},
                    status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.get(user=request.user, author=author).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        follows = request.user.follows.all()
        authors = User.objects.filter(followers__in=follows)
        page = self.paginate_queryset(authors)
        if page is not None:
            serializer = UserFollowSerializer(page,
                                              context={'request': request},
                                              many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserFollowSerializer(authors,
                                          context={'request': request},
                                          many=True)
        return Response(serializer.data)
