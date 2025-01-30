from .apps import NotesConfig
from django.urls import path
from .views import (
    PaidContentCreateView,
    PaidContentDetailView,
    PaidContentUpdateView,
    PaidContentDeleteView,
    PaidContentListView,
    FreeContentCreateView,
    FreeContentDetailView,
    FreeContentUpdateView,
    FreeContentDeleteView,
    FreeContentListView,
    MyContentListView,
    buy_content_subscription,
    contacts,
)

app_name = NotesConfig.name

urlpatterns = [
    path("content/my_content/", MyContentListView.as_view(), name="my_content"),
    path("content/free/", FreeContentListView.as_view(), name="free_content_list"),
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
        FreeContentDeleteView.as_view(),
        name="free_content_destroy",
    ),
    path("content/paid/", PaidContentListView.as_view(), name="paid_content_list"),
    path(
        "content/paid/create/",
        PaidContentCreateView.as_view(),
        name="paid_content_create",
    ),
    path(
        "content/paid/<int:pk>/",
        PaidContentDetailView.as_view(),
        name="paid_content_retrieve",
    ),
    path(
        "content/paid/<int:pk>/update/",
        PaidContentUpdateView.as_view(),
        name="paid_content_update",
    ),
    path(
        "content/paid/<int:pk>/destroy/",
        PaidContentDeleteView.as_view(),
        name="paid_content_destroy",
    ),
    path(
        "content/paid/<int:pk>/buy/",
        buy_content_subscription,
        name="buy_paid_content",
    ),
    path(
        "contacts/",
        contacts,
        name="contacts",
    ),
]
