"""Config Url Paths."""
# Third-Party Libraries
from django.urls import include, path

from .views import HomePageView

urlpatterns = [
    path("api/", include("api.urls")),
    path("auth/", include("auth.urls")),
    path("", HomePageView.as_view(), name="home"),
]
