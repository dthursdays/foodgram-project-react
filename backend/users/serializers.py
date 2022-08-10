from django.contrib.auth import get_user_model
from djoser.serializers import UserSerializer, UserCreateSerializer

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')
        read_only_fields = ('id', )


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'id', 'first_name', 'last_name')
        read_only_fields = ('id', )
