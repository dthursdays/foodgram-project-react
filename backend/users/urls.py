from django.urls import include, path
from rest_framework import routers

from .views import CustomUserViewSet

app_name = 'users'

router_v1 = routers.DefaultRouter()
router_v1.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
