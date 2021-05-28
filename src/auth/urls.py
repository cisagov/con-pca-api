"""Authentication urls."""
# Third-Party Libraries
from django.urls import path

# cisagov Libraries
import auth.views

urlpatterns = [
    path(
        "register/",
        auth.views.RegisterView.as_view(),
        name="auth_register",
    ),
    path(
        "login/",
        auth.views.LoginView.as_view(),
        name="auth_login",
    ),
    path(
        "refresh/",
        auth.views.RefreshTokenView.as_view(),
        name="auth_refresh",
    ),
]
