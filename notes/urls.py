from .apps import NotesConfig
from django.urls import path
from .views import (
    PaidContentCreateAPIView,
    PaidContentRetrieveAPIView,
    PaidContentUpdateAPIView,
    PaidContentDestroyAPIView,
    PaidContentListAPIView,
    FreeContentCreateView,
    FreeContentDetailView,
    FreeContentUpdateView,
    FreeContentDestroyAPIView,
    FreeContentListView,
)

app_name = NotesConfig.name

urlpatterns = [
    path(
        "content/free/",
        FreeContentListView.as_view(),
        name="free_content_list"
    ),
    path(
        "content/free/create/",
        FreeContentCreateView.as_view(),
        name="free_content_create",
    ),
    path(
        "content/free/<int:pk>/",
        FreeContentDetailView.as_view(),
        name="free_content_retrieve",
    ),
    path(
        "content/free/<int:pk>/update/",
        FreeContentUpdateView.as_view(),
        name="free_content_update",
    ),
    path(
        "content/free/<int:pk>/destroy/",
        FreeContentDestroyAPIView.as_view(),
        name="free_content_destroy",
    ),
    path(
        "content/paid/",
        PaidContentListAPIView.as_view(),
        name="paid_content_list"
    ),
    path(
        "content/paid/create/",
        PaidContentCreateAPIView.as_view(),
        name="paid_content_create",
    ),
    path(
        "content/paid/<int:pk>/",
        PaidContentRetrieveAPIView.as_view(),
        name="paid_content_retrieve",
    ),
    path(
        "content/paid/<int:pk>/update/",
        PaidContentUpdateAPIView.as_view(),
        name="paid_content_update",
    ),
    path(
        "content/paid/<int:pk>/destroy/",
        PaidContentDestroyAPIView.as_view(),
        name="paid_content_destroy",
    ),
]
