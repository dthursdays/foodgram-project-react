from .models import User
from djoser.views import UserViewSet


class CustomUserViewSet(UserViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post']

    def get_queryset(self):
        return self.queryset
