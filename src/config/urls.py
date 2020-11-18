"""Config Url Paths."""
# Third-Party Libraries
from django.contrib import admin
from django.urls import include, path

from .views import HomePageView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("reports/", include("reports.urls")),
    path("api/", include("api.urls")),
    path("", HomePageView.as_view(), name="home"),
]
