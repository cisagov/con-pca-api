# Based on https://github.com/labd/django-cognito-jwt under MIT license
import logging
import time
import hmac
import hashlib

from django.apps import apps as django_apps
from django.conf import settings
from config.settings import LOCAL_API_KEY
from django.utils.encoding import smart_text
from django.utils.translation import ugettext as _
from rest_framework import exceptions
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from authentication.validator import TokenError, TokenValidator

logger = logging.getLogger(__name__)


class JSONWebTokenAuthentication(BaseAuthentication):
    """Token based authentication using the JSON Web Token standard."""

    def authenticate(self, request):
        """Entrypoint for Django Rest Framework"""
        print(settings.COGNITO_DEPLOYMENT_MODE)

        gp_sign = request.headers.get("X-Gophish-Signature")
        if gp_sign:
            gp_sign = gp_sign.split("=")[-1]
            digest = hmac.new(
                LOCAL_API_KEY.encode(), request.body, hashlib.sha256
            ).hexdigest()
            if digest == gp_sign:
                user = {"username": "gophish", "groups": {"develop"}}
                token = "Empty token"
                return (user, token)

        if settings.COGNITO_DEPLOYMENT_MODE == "Development":
            print("Using develop authorization")
            user = {"username": "developer user", "groups": {"develop"}}
            token = "Empty token"
            return (user, token)

        if (
            LOCAL_API_KEY
            and get_authorization_header(request).decode() == LOCAL_API_KEY
        ):
            print("Local api authorization")
            user = {"username": "api", "groups": {"develop"}}
            token = "Empty token"
            return (user, token)

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
            print(msg)
            raise exceptions.AuthenticationFailed(msg)
        if jwt_payload["client_id"] != settings.COGNITO_AUDIENCE:
            msg = _(
                "Client_ID does not match the applications, please"
                "ensure you are logged into the correct AWS account"
            )
            print(msg)
            raise exceptions.AuthenticationFailed(msg)

        # USER_MODEL = self.get_user_model()
        # user = USER_MODEL.objects.get_or_create_for_cognito(jwt_payload)
        if "cognito:groups" in jwt_payload:
            user = {
                "username": jwt_payload["username"],
                "groups": jwt_payload["cognito:groups"],
            }
        else:
            user = {"username": jwt_payload["username"], "groups": "None"}
        return (user, jwt_token)

    def get_user_model(self):
        user_model = getattr(settings, "COGNITO_USER_MODEL", settings.AUTH_USER_MODEL)
        return django_apps.get_model(user_model, require_ready=False)

    def get_jwt_token(self, request):
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
        return TokenValidator(
            settings.COGNITO_AWS_REGION,
            settings.COGNITO_USER_POOL,
            settings.COGNITO_AUDIENCE,
        )

    def authenticate_header(self, request):
        """
        Method required by the DRF in order to return 401 responses for authentication failures, instead of 403.
        More details in https://www.django-rest-framework.org/api-guide/authentication/#custom-authentication.
        """
        return "Bearer: api"
