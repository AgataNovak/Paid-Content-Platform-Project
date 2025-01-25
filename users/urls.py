from django.urls import path
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from users.apps import UsersConfig
from rest_framework_simplejwt.views import TokenObtainPairView
from users.views import (
    UserCreateView,
    UserProfileViewSet,
    profile,
    CustomLogoutView,
    CustomLoginView,
    ServiceSubscriptionCreateView,
    ServiceSubscriptionListAPIView,
)

app_name = UsersConfig.name

router = routers.SimpleRouter()
router.register(
    "users/my_profile/",
    UserProfileViewSet,
    basename="profile_view"
)

urlpatterns = [
    path(
        "users/token/",
        TokenObtainPairView.as_view(),
        name="token"
    ),
    path(
        "users/register/",
        UserCreateView.as_view(),
        name="register"
    ),
    path(
        "users/login/",
        CustomLoginView.as_view(),
        name='login',
    ),
    path(
        "users/logout/",
        CustomLogoutView.as_view(),
        name='logout',
    ),
    path(
        "users/service/subscriptions/",
        ServiceSubscriptionListAPIView.as_view(),
        name="service_subscriptions",
    ),
    path(
        "users/service/subscribe/",
        ServiceSubscriptionCreateView.as_view(),
        name="service_subscribe",
    ),
    path(
        "users/profile/", profile,
        name="user_profile",
    )
]

urlpatterns += router.urls
