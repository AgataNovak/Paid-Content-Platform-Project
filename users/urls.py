from django.urls import path
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenObtainPairView
from users.views import (
    UserCreateView,
    profile,
    CustomLogoutView,
    CustomLoginView,
    buy_subscription,
)

app_name = UsersConfig.name

urlpatterns = [
    path("users/token/", TokenObtainPairView.as_view(), name="token"),
    path("users/register/", UserCreateView.as_view(), name="register"),
    path(
        "users/login/",
        CustomLoginView.as_view(),
        name="login",
    ),
    path(
        "users/logout/",
        CustomLogoutView.as_view(),
        name="logout",
    ),
    path(
        "users/service/subscribe/",
        buy_subscription,
        name="service_subscribe",
    ),
    path(
        "users/profile/",
        profile,
        name="user_profile",
    ),
]
