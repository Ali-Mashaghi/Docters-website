from django.urls import path

from .views import DoctorConsultationView, DoctorDetailView, DoctorListView, HomeView

app_name = "doctors"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("doctors/", DoctorListView.as_view(), name="doctor_list"),
    path(
        "doctors/<str:slug>/consultation-form/",
        DoctorConsultationView.as_view(),
        name="doctor_consultation",
    ),
    path("doctors/<str:slug>/", DoctorDetailView.as_view(), name="doctor_detail"),
]
