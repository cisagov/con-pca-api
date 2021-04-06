"""Backend Authentication."""
# Based on https://github.com/labd/django-cognito-jwt under MIT license
# Standard Python Libraries
import hashlib
import hmac
import os
import time

# Third-Party Libraries
from django.apps import apps as django_apps
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

# cisagov Libraries
from authentication.validator import TokenError, TokenValidator
from config import settings


class JSONWebTokenAuthentication(BaseAuthentication):
    """JSONWebTokenAuthentication."""

    def authenticate(self, request):
        """Authenticate Request."""
        # Gophish Authentication
        gp_sign = request.headers.get("X-Gophish-Signature")
        if gp_sign:
            gp_sign = gp_sign.split("=")[-1]
            digest = hmac.new(
                settings.LOCAL_API_KEY.encode(), request.body, hashlib.sha256
            ).hexdigest()
            if digest == gp_sign:
                user = {"username": "gophish", "groups": {"develop"}}
                return (user, "Empty token")

        # Development Authentication
        if os.environ.get("COGNITO_DEPLOYMENT_MODE") == "Development":
            user = {"username": "developer user", "groups": {"develop"}}
            return (user, "Empty token")

        # Local Authentication
        if (
            settings.LOCAL_API_KEY
            and get_authorization_header(request).decode() == settings.LOCAL_API_KEY
        ):
            user = {"username": "api", "groups": {"develop"}}
            return (user, "Empty token")

        # Reports authentication with bearer
        if (
            settings.LOCAL_API_KEY
            and get_authorization_header(request).decode().split(" ")[-1]
            == settings.LOCAL_API_KEY
        ):
            user = {"usuername": "reports", "groups": {"develop"}}
            return (user, "Empty token")

        jwt_token = self.get_jwt_token(request)
        if jwt_token is None:
            raise exceptions.AuthenticationFailed()

        # Authenticate token
        try:
            token_validator = self.get_token_validator(request)
            jwt_payload = token_validator.validate(jwt_token)
        except TokenError:
            raise exceptions.AuthenticationFailed()

        # Ensure jwt is not expired
        if (jwt_payload["exp"] - int(time.time())) < 0:
            msg = "Token has expired, please log back in"
            raise exceptions.AuthenticationFailed(msg)

        if jwt_payload["client_id"] != os.environ.get("COGNITO_AUDIENCE"):
            msg = _(
                "Client_ID does not match the applications, please"
                "ensure you are logged into the correct AWS account"
            )
            raise exceptions.AuthenticationFailed(msg)

        if "cognito:groups" in jwt_payload:
            user = {
                "username": jwt_payload["username"],
                "groups": jwt_payload["cognito:groups"],
            }
        else:
            user = {"username": jwt_payload["username"], "groups": "None"}
        return (user, jwt_token)

    def get_user_model(self):
        """Get User Model."""
        user_model = getattr(settings, "COGNITO_USER_MODEL", settings.AUTH_USER_MODEL)
        return django_apps.get_model(user_model, require_ready=False)

    def get_jwt_token(self, request):
        """Get JWT Token from request."""
        auth = get_authorization_header(request).split()
        if not auth or smart_text(auth[0].lower()) != "bearer":
            return None

        if len(auth) == 1:
            msg = _("Invalid Authorization header. No credentials provided.")
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth) > 2:
            msg = _(
                "Invalid Authorization header. Credentials string "
                "should not contain spaces."
            )
            raise exceptions.AuthenticationFailed(msg)

        return auth[1]

    def get_token_validator(self, request):
        """Get Token Validator."""
        return TokenValidator(
            settings.COGNITO_AWS_REGION,
            settings.COGNITO_USER_POOL,
            os.environ.get("COGNITO_AUDIENCE"),
        )

    def authenticate_header(self, request):
        """Authenticate Header."""
        # Method required by the DRF in order to return 401 responses for authentication failures, instead of 403.
        # More details in https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication.
        return "Bearer: api"
