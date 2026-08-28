from django.urls import path

from .views import (
    ArticleCreateView,
    ArticleDeleteView,
    ArticleListView,
    ArticleTogglePublishView,
    ArticleUpdateView,
    ConsultationDetailView,
    ConsultationListView,
    ConsultationStatusUpdateView,
    DashboardView,
    ManagerAssignView,
    ManagerCreateView,
    ManagerDeleteView,
    ManagerListView,
)

app_name = "dashboard"

urlpatterns = [
    path("", DashboardView.as_view(), name="home"),
    path(
        "consultations/",
        ConsultationListView.as_view(),
        name="consultations",
    ),
    path(
        "consultations/<int:pk>/",
        ConsultationDetailView.as_view(),
        name="consultation_detail",
    ),
    path(
        "consultations/<int:pk>/status/",
        ConsultationStatusUpdateView.as_view(),
        name="consultation_status_update",
    ),
    path("managers/", ManagerListView.as_view(), name="managers"),
    path("managers/create/", ManagerCreateView.as_view(), name="manager_create"),
    path(
        "managers/<int:pk>/assign/",
        ManagerAssignView.as_view(),
        name="manager_assign",
    ),
    path(
        "managers/<int:pk>/delete/",
        ManagerDeleteView.as_view(),
        name="manager_delete",
    ),
    path("articles/", ArticleListView.as_view(), name="articles"),
    path("articles/create/", ArticleCreateView.as_view(), name="article_create"),
    path(
        "articles/<int:pk>/edit/",
        ArticleUpdateView.as_view(),
        name="article_edit",
    ),
    path(
        "articles/<int:pk>/delete/",
        ArticleDeleteView.as_view(),
        name="article_delete",
    ),
    path(
        "articles/<int:pk>/toggle-publish/",
        ArticleTogglePublishView.as_view(),
        name="article_toggle_publish",
    ),
]
