from django.urls import path

from .views import (
    ArticleCreateView,
    ArticleDeleteView,
    ArticleListView,
    ArticleTogglePublishView,
    ArticleUpdateView,
    ConsultationDetailView,
    ConsultationDeleteView,
    ConsultationListView,
    ConsultationStatusUpdateView,
    DashboardView,
    DoctorCreateView,
    DoctorDeleteView,
    DoctorListView,
    DoctorToggleActiveView,
    DoctorUpdateView,
    ManagerAssignView,
    ManagerCreateView,
    ManagerDeleteView,
    ManagerListView,
    PortfolioDeleteView,
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
    path(
        "consultations/<int:pk>/delete/",
        ConsultationDeleteView.as_view(),
        name="consultation_delete",
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
    path("doctors/", DoctorListView.as_view(), name="doctors"),
    path("doctors/create/", DoctorCreateView.as_view(), name="doctor_create"),
    path("doctors/<int:pk>/edit/", DoctorUpdateView.as_view(), name="doctor_edit"),
    path("doctors/<int:pk>/delete/", DoctorDeleteView.as_view(), name="doctor_delete"),
    path(
        "doctors/<int:pk>/toggle-active/",
        DoctorToggleActiveView.as_view(),
        name="doctor_toggle_active",
    ),
    path(
        "doctors/<int:doctor_pk>/portfolios/<int:pk>/delete/",
        PortfolioDeleteView.as_view(),
        name="portfolio_delete",
    ),
]
