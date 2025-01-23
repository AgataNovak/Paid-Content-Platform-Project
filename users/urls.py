from django.urls import path
from rest_framework import routers
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenObtainPairView
from users.views import (
    UserCreateApiView,
    UserProfileViewSet,
    ServiceSubscriptionView
)

app_name = UsersConfig.name

router = routers.SimpleRouter()
router.register('users/profile/', UserProfileViewSet, basename='profile_view')
urlpatterns = [
    path("users/login/", TokenObtainPairView.as_view(), name="login"),
    path("users/register/", UserCreateApiView.as_view(), name="register"),
    path("users/service_subscription/", ServiceSubscriptionView.as_view(), name="service_subscription"),
]

urlpatterns += router.urls
