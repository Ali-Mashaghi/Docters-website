from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("apps.doctors.urls")),
    path("articles/", include("apps.articles.urls")),
    path("consultations/", include("apps.consultations.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG or settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
